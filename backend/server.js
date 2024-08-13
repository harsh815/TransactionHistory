const express = require('express');
const { spawn } = require('child_process');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const moment = require('moment');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(bodyParser.json());

mongoose.connect(process.env.MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

const transactionAggregateSchema = new mongoose.Schema({
  userId: String,
  date: Date,
  category: String,
  amount: Number
});

const jobSchema = new mongoose.Schema({
  userId: String,
  status: {
    type: String,
    enum: ['STARTED', 'COMPLETED', 'FAILED'],
    default: 'STARTED'
  },
  startTime: { type: Date, default: Date.now },
  endTime: Date,
  error: String
});

const TransactionAggregate = mongoose.model('TransactionAggregate', transactionAggregateSchema);
const Job = mongoose.model('Job', jobSchema);

app.post('/api/sms', async (req, res) => {
  try {
    const { userId, smsData } = req.body;
    
    const job = new Job({ userId });
    await job.save();

    processSMSData(job._id, userId, smsData);

    res.status(202).json({ 
      message: 'Data received and processing initiated',
      jobId: job._id 
    });
  } catch (error) {
    console.error('Error processing SMS data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/job/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const job = await Job.findById(jobId);
    
    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }
    
    res.json({
      jobId: job._id,
      status: job.status,
      startTime: job.startTime,
      endTime: job.endTime,
      error: job.error
    });
  } catch (error) {
    console.error('Error retrieving job status:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/user/:userId/summary', async (req, res) => {
  try {
    const { userId } = req.params;
    const { timeframe } = req.query;
    
    const { startDate, endDate } = getDateRangeFromTimeframe(timeframe);

    const aggregates = await TransactionAggregate.aggregate([
      {
        $match: {
          userId: userId,
          date: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: '$category',
          totalAmount: { $sum: '$amount' },
          count: { $sum: 1 }
        }
      }
    ]);

    const totalSMS = aggregates.reduce((sum, agg) => sum + agg.count, 0);
    const categoryAmounts = Object.fromEntries(
      aggregates.map(agg => [agg._id, agg.totalAmount])
    );

    res.json({
      totalSMS,
      lastUpdated: new Date().toISOString(),
      aggregate: {
        period: timeframe,
        totalSMS,
        categoryAmounts
      }
    });
  } catch (error) {
    console.error('Error retrieving summary:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function getDateRangeFromTimeframe(timeframe) {
  const endDate = moment().endOf('day');
  let startDate;

  switch (timeframe) {
    case 'week':
      startDate = moment().subtract(1, 'weeks').startOf('day');
      break;
    case 'month':
      startDate = moment().subtract(1, 'months').startOf('day');
      break;
    case 'year':
      startDate = moment().subtract(1, 'years').startOf('day');
      break;
    default:
      throw new Error('Invalid timeframe');
  }

  return { startDate: startDate.toDate(), endDate: endDate.toDate() };
}

async function updateAggregates(userId, categorizedSMS) {
  for (const sms of categorizedSMS) {
    await TransactionAggregate.updateOne(
      { 
        userId: userId, 
        date: new Date(sms.timestamp), 
        category: sms.category 
      },
      { 
        $inc: { amount: sms.amount } 
      },
      { upsert: true }
    );
  }
}

function processSMSData(jobId, userId, smsData) {
  const sparkSubmit = spawn('spark-submit', ['spark_prediction.py']);
  
  sparkSubmit.stdin.write(JSON.stringify(smsData));
  sparkSubmit.stdin.end();

  let predictions = '';
  sparkSubmit.stdout.on('data', (data) => {
    predictions += data.toString();
  });

  sparkSubmit.on('close', async (code) => {
    try {
      if (code !== 0) {
        await Job.findByIdAndUpdate(jobId, { 
          status: 'FAILED', 
          endTime: new Date(),
          error: `Spark job exited with code ${code}`
        });
        return;
      }

      const categorizedSMS = JSON.parse(predictions);
      await updateAggregates(userId, categorizedSMS);

      await Job.findByIdAndUpdate(jobId, { 
        status: 'COMPLETED', 
        endTime: new Date() 
      });
    } catch (error) {
      console.error('Error processing SMS data:', error);
      await Job.findByIdAndUpdate(jobId, { 
        status: 'FAILED', 
        endTime: new Date(),
        error: error.message
      });
    }
  });
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});