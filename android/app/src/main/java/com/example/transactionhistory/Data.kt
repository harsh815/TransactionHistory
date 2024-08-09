package com.example.transactionhistory

data class SMS(
    val sender: String,
    val timestamp: Long,
    val content: String
)

data class SMSDataRequest(
    val userId: String,
    val smsData: List<SMS>,
    val lastTimestamp: Long
)

data class JobResponse(
    val message: String,
    val jobId: String
)

data class JobStatus(
    val jobId: String,
    val status: String,
    val startTime: String,
    val endTime: String?,
    val error: String?
)

data class UserSummary(
    val totalSMS: Int,
    val lastUpdated: String,
    val weeklyAggregates: List<Aggregate>?,
    val monthlyAggregates: List<Aggregate>?,
    val yearlyAggregates: List<Aggregate>?
)

data class Aggregate(
    val period: String, // This could be a week, month, or year depending on the aggregate type
    val totalSMS: Int,
    val categoryCounts: Map<String, Int>
)