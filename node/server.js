const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const { spawn } = require('child_process');
const Minio = require('minio');

dotenv.config();

const app = express();
app.use(bodyParser.json());

// MinIO client setup
const minioClient = new Minio.Client({
    endPoint: 'localhost',
    port: 9000,
    useSSL: false,
    accessKey: process.env.MINIO_ACCESS_KEY,
    secretKey: process.env.MINIO_SECRET_KEY
});

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI).then(() => {
  console.log('Connected to MongoDB');
}).catch((err) => {
  console.error('MongoDB connection error:', err);
});

// MongoDB Schemas
const userAggregateSchema = new mongoose.Schema({
  userId: String,
  totalSMS: Number,
  lastUpdated: Date,
  weeklyAggregates: [{
    week: Date,
    totalSMS: Number,
    categoryCounts: Map
  }],
  monthlyAggregates: [{
    month: Date,
    totalSMS: Number,
    categoryCounts: Map
  }],
  yearlyAggregates: [{
    year: Number,
    totalSMS: Number,
    categoryCounts: Map
  }]
});

const UserAggregate = mongoose.model('UserAggregate', userAggregateSchema);

const sparkJobSchema = new mongoose.Schema({
  jobId: String,
  userId: String,
  status: {
    type: String,
    enum: ['STARTED', 'COMPLETED', 'FAILED'],
    default: 'STARTED'
  },
  error: String,
  startTime: Date,
  endTime: Date
});

const SparkJob = mongoose.model('SparkJob', sparkJobSchema);

async function ensureBucketExists(bucketName) {
  if (!bucketName) {
    throw new Error("Bucket name is undefined. Check your .env file.");
  }
  try {
    const exists = await minioClient.bucketExists(bucketName);
    if (!exists) {
      await minioClient.makeBucket(bucketName);
      console.log(`Bucket '${bucketName}' created successfully.`);
    } else {
      console.log(`Bucket '${bucketName}' already exists.`);
    }
  } catch (err) {
    console.error(`Error checking/creating bucket '${bucketName}':`, err);
    throw err;
  }
}

function startSparkJob(bucketName, objectName, userId, jobId) {
  const sparkJobScript = 'process_sms_data.py';
  const sparkSubmit = spawn('spark-submit', [
    '--master', 'local[*]',
    sparkJobScript,
    bucketName,
    objectName,
    userId,
    jobId
  ]);

  sparkSubmit.stdout.on('data', (data) => {
    console.log(`Spark job output: ${data}`);
  });

  sparkSubmit.stderr.on('data', (data) => {
    console.error(`Spark job error: ${data}`);
  });

  sparkSubmit.on('close', async (code) => {
    console.log(`Spark job exited with code ${code}`);
    
    await SparkJob.findOneAndUpdate(
      { jobId },
      { 
        status: code === 0 ? 'COMPLETED' : 'FAILED',
        endTime: new Date(),
        ...(code !== 0 && { error: `Job exited with code ${code}` })
      }
    );
  });
}

app.post('/api/sms', async (req, res) => {
  try {
    const { userId, smsData } = req.body;
    
    const bucketName = process.env.MINIO_BUCKET_NAME;
    const objectName = `raw-sms/${userId}/${Date.now()}.json`;
    
    await minioClient.putObject(bucketName, objectName, JSON.stringify(smsData));
    
    const jobId = new mongoose.Types.ObjectId().toString();
    const newJob = new SparkJob({
      jobId,
      userId,
      startTime: new Date()
    });
    await newJob.save();

    startSparkJob(bucketName, objectName, userId, jobId);
    
    res.status(202).json({ 
      message: 'Data received and processing initiated',
      jobId: jobId
    });
  } catch (error) {
    console.error('Error processing SMS data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/job/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const job = await SparkJob.findOne({ jobId });
    
    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }
    
    res.json({
      jobId: job.jobId,
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
    const { timeframe } = req.query; // 'weekly', 'monthly', or 'yearly'
    
    const userAggregate = await UserAggregate.findOne({ userId });
    
    if (!userAggregate) {
      return res.status(404).json({ error: 'No data found for this user' });
    }

    let summary;
    switch(timeframe) {
      case 'weekly':
        summary = userAggregate.weeklyAggregates;
        break;
      case 'monthly':
        summary = userAggregate.monthlyAggregates;
        break;
      case 'yearly':
        summary = userAggregate.yearlyAggregates;
        break;
      default:
        summary = {
          totalSMS: userAggregate.totalSMS,
          lastUpdated: userAggregate.lastUpdated
        };
    }
    
    res.json(summary);
  } catch (error) {
    console.error('Error retrieving summary:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

ensureBucketExists(process.env.MINIO_BUCKET_NAME)
  .then(() => {
    const port = process.env.PORT || 3000;
    app.listen(port, () => {
      console.log(`Server running on port ${port}`);
    });
  })
  .catch(err => {
    console.error('Failed to start server due to MinIO bucket error:', err);
    process.exit(1);
  });