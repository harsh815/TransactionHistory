package com.example.transactionhistory

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.example.transactionhistory.RetrofitClient.apiService
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private val READ_SMS_PERMISSION_CODE = 123
    private lateinit var smsReader: SMSReader

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        smsReader = SMSReader(this)

        setupViews()
    }

    private fun setupViews() {
        findViewById<Button>(R.id.syncDataButton).setOnClickListener {
            if (checkSmsPermission()) {
                syncSmsData()
            } else {
                requestSmsPermission()
            }
        }

        findViewById<Button>(R.id.viewSummaryButton).setOnClickListener {
            launchSummaryActivity()
        }
    }

    private fun launchSummaryActivity() {
        val intent = Intent(this, SummaryActivity::class.java)
        intent.putExtra("USER_ID", getUserId())
        startActivity(intent)
    }

    private fun checkSmsPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_SMS
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestSmsPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.READ_SMS),
            READ_SMS_PERMISSION_CODE
        )
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == READ_SMS_PERMISSION_CODE && grantResults.isNotEmpty()
            && grantResults[0] == PackageManager.PERMISSION_GRANTED
        ) {
            syncSmsData()
        } else {
            Toast.makeText(this, "SMS permission denied", Toast.LENGTH_LONG).show()
        }
    }

    private fun syncSmsData() {
        lifecycleScope.launch {
            try {
                val userId = getUserId()
                val newSms = smsReader.readNewSMS()
                val request = SMSDataRequest(userId, newSms, System.currentTimeMillis())
                val response = apiService.sendSmsData(request)
                if (response.isSuccessful) {
                    val jobResponse = response.body()
                    jobResponse?.let {
                        Toast.makeText(this@MainActivity, "Job started with ID: ${it.jobId}", Toast.LENGTH_LONG).show()
                        // You might want to store this jobId to check its status later
                    }
                } else {
                    Toast.makeText(this@MainActivity, "Failed to sync SMS data", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }


    private fun getUserId(): String {
        val sharedPrefs = getSharedPreferences("AppPrefs", MODE_PRIVATE)
        var userId = sharedPrefs.getString("userId", null)
        if (userId == null) {
            userId = java.util.UUID.randomUUID().toString()
            sharedPrefs.edit().putString("userId", userId).apply()
        }
        return userId
    }


}