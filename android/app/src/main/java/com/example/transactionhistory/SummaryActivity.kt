package com.example.transactionhistory

import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.transactionhistory.RetrofitClient.apiService
import kotlinx.coroutines.launch
import java.util.Date

class SummaryActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: SummaryAdapter
    private lateinit var timeframeSpinner: Spinner


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_summary)

        recyclerView = findViewById(R.id.summaryRecyclerView)
        adapter = SummaryAdapter()
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)

        timeframeSpinner = findViewById(R.id.timeframeSpinner)
        setupTimeframeSpinner()

        fetchSummary("weekly") // Initial fetch with weekly timeframe

    }

    private fun setupTimeframeSpinner() {
        ArrayAdapter.createFromResource(
            this,
            R.array.timeframe_array,
            android.R.layout.simple_spinner_item
        ).also { adapter ->
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
            timeframeSpinner.adapter = adapter
        }

        timeframeSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>, view: View, position: Int, id: Long) {
                val selectedTimeframe = parent.getItemAtPosition(position).toString().toLowerCase()
                fetchSummary(selectedTimeframe)
            }

            override fun onNothingSelected(parent: AdapterView<*>) {}
        }
    }

    private fun fetchSummary(timeframe: String) {
        lifecycleScope.launch {
            try {
                val userId = intent.getStringExtra("USER_ID")?:"1" //handle this later, we have ? in userId, passing 1 as default
                val response = apiService.getUserSummary(userId, timeframe) // You can change the timeframe as needed
                if (response.isSuccessful) {
                    val summary = response.body()
                    summary?.let {
                        displaySummary(it, timeframe)
                    }
                } else {
                    Toast.makeText(this@SummaryActivity, "Failed to fetch summary", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@SummaryActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun displaySummary(summary: UserSummary, timeframe: String) {
        findViewById<TextView>(R.id.totalSmsTextView).text = "Total SMS: ${summary.totalSMS}"
        findViewById<TextView>(R.id.lastUpdatedTextView).text = "Last Updated: ${summary.lastUpdated}"

        val aggregates = when (timeframe) {
            "weekly" -> summary.weeklyAggregates
            "monthly" -> summary.monthlyAggregates
            "yearly" -> summary.yearlyAggregates
            else -> null
        }

        aggregates?.let {
            adapter.submitList(it)
        }
    }

}