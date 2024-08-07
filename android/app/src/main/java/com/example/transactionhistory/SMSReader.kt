package com.example.transactionhistory

import android.content.Context
import android.provider.Telephony
import java.util.*

class SMSReader(private val context: Context) {
    private val sharedPrefs = context.getSharedPreferences("SMSReaderPrefs", Context.MODE_PRIVATE)

    fun readNewSMS(): List<SMS> {
        val lastProcessedTimestamp = sharedPrefs.getLong("lastProcessedTimestamp", 0)
        val smsList = mutableListOf<SMS>()
        val cursor = context.contentResolver.query(
            Telephony.Sms.CONTENT_URI,
            null,
            "${Telephony.Sms.DATE} > ?",
            arrayOf(lastProcessedTimestamp.toString()),
            "${Telephony.Sms.DATE} ASC"
        )

        cursor?.use {
            val senderIndex = it.getColumnIndex(Telephony.Sms.ADDRESS)
            val timestampIndex = it.getColumnIndex(Telephony.Sms.DATE)
            val bodyIndex = it.getColumnIndex(Telephony.Sms.BODY)

            while (it.moveToNext()) {
                val sender = it.getString(senderIndex)
                val timestamp = it.getLong(timestampIndex)
                val content = it.getString(bodyIndex)
                smsList.add(SMS(sender, timestamp, content))
            }

            if (smsList.isNotEmpty()) {
                val newLastProcessedTimestamp = smsList.last().timestamp
                sharedPrefs.edit().putLong("lastProcessedTimestamp", newLastProcessedTimestamp).apply()
            }
        }

        return smsList
    }
}