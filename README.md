# SMS Analysis and Transaction Categorization System
## Overview

This project is a comprehensive system for analyzing SMS messages,  focusing on financial transactions. It categorizes messages, provides insights into spending patterns, and offers summaries over different time frames (weekly, monthly, yearly).

## Design Details
<img src="https://github.com/user-attachments/assets/d2a3d77e-47a8-4870-852b-3addc8f187e1" width="400" />
<img src="https://github.com/user-attachments/assets/18c214f5-75f3-4bed-92c1-b716b317749a" width="400" />
<img src="https://github.com/user-attachments/assets/0b27847d-f1c2-4aaa-8178-b5da942233c1" width="800" />

## Features

- Android app for SMS data collection and summary display
- Automatic SMS categorization using machine learning
- Scalable backend using Spark for processing large volumes of SMS data
- User-friendly transaction history summaries
- Secure data handling and privacy protection

## Technology Stack

- **Frontend**: Android (Kotlin)
- **Backend**: Node.js, Express
- **Data Storage**: 
  - MongoDB for processed data and aggregates
  - MinIO(S3 API compatible) for raw SMS data storage
- **Data Processing**: EMR(Apache Spark locally)
- **Machine Learning**: Python (scikit-learn for TF-IDF and K-means clustering)
- **API**: RESTful API using Retrofit (Android) and Express (Server)

## Setup Instructions

### Prerequisites(for local run)

- Node.js and npm
- Java Development Kit (JDK)
- Android Studio
- MongoDB
- MinIO
- Apache Spark

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sms-analysis-project.git
   cd sms-analysis-project/server
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the necessary credentials and configurations

4. Start the server:
   ```
   npm start
   ```

### Android App Setup

1. Open the project in Android Studio
2. Update the `BASE_URL` in `RetrofitClient.kt` to point to your node.js server
3. Build and run the app on an emulator or physical device

### Data Processing Setup

1. Ensure Apache Spark is installed and configured
2. Update Spark configurations in the `.env` file
3. Ensure MinIO server is running and update env

## Usage

1. Launch the Android app
2. Grant SMS read permissions
3. Use the "Sync SMS Data" button to send SMS data to the server
4. View transaction summaries using the "View Summary" button

## API Endpoints

- `POST /api/sms`: Send SMS data for processing
- `GET /api/job/:jobId`: Check the status of a processing job
- `GET /api/user/:userId/summary`: Retrieve user summary data

## TODO
Docker Containerisation to make setup easier

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.


