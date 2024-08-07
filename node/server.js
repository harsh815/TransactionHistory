const express = require('express');
const bodyParser = require('body-parser');
const winston = require('winston');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();

// Middleware
app.use(bodyParser.json());

// Configure Winston logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}


// Route Handlers
app.post('/api/sms', async (req, res) => {
  try {
    const { userId, smsData } = req.body;
        
    const metadataEntries = smsData.map(sms => ({
      userId,
      smsId: sms.id,
      timestamp: new Date(sms.timestamp),
      processedStatus: 'pending'
    }));    
    res.status(200).json({ message: 'Data received and processing initiated' });
  } catch (error) {
    logger.error('Error processing SMS data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/user/:userId/summary', async (req, res) => {
    try {
      res.json({ 
        userId : "123", 
        summaries: [
            {
                category: "food",
                totalAmount: 5000,
                transactionCount: 50,
                lastUpdated: "04/07/2024"
            },
            {
                category: "travel",
                totalAmount: 6000,
                transactionCount: 50,
                lastUpdated: "04/07/2024"
            },
            {
                category: "rent",
                totalAmount: 25000,
                transactionCount: 50,
                lastUpdated: "04/07/2024"
            },
            {
                category: "services",
                totalAmount: 5000,
                transactionCount: 50,
                lastUpdated: "04/07/2024"
            }
        ],
        lastUpdated: new Date()
      });
    } catch (error) {
      logger.error('Error retrieving summary:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });



// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  logger.info(`Server running on port ${port}`);
});
