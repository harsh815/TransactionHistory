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
data class TransactionSummary(
    val category: String,
    val totalAmount: Double,
    val transactionCount: Int,
    val lastUpdated: String
)

data class UserSummary(
    val userId: String,
    val summaries: List<TransactionSummary>,
    val lastUpdated: String
)
