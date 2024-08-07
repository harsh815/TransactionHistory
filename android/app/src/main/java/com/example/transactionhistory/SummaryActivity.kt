package com.example.transactionhistory

import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.launch

class SummaryActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: SummaryAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_summary)

        recyclerView = findViewById(R.id.summaryRecyclerView)
        adapter = SummaryAdapter()
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)

        fetchSummary()
    }

    private fun fetchSummary() {
        lifecycleScope.launch {
            try {
                val userId = intent.getStringExtra("USER_ID") ?: run {
                    Toast.makeText(this@SummaryActivity, "Error: User ID not provided", Toast.LENGTH_SHORT).show()
                    finish()
                } // Implement this function to get the user ID
                val response = RetrofitClient.apiService.getUserSummary(userId.toString())
                if (response.isSuccessful) {
                    response.body()?.let { userSummary ->
                        adapter.submitList(userSummary.summaries)
                        updateLastUpdatedText(userSummary.lastUpdated)
                    }
                } else {
                    Toast.makeText(this@SummaryActivity, "Failed to fetch summary", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@SummaryActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun updateLastUpdatedText(lastUpdated: String) {
        findViewById<TextView>(R.id.lastUpdatedTextView).text = "Last Updated: $lastUpdated"
    }
}