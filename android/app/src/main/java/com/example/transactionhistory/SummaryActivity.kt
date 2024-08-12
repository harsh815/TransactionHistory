package com.example.transactionhistory

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.transactionhistory.RetrofitClient.apiService
import kotlinx.coroutines.launch

class SummaryActivity : AppCompatActivity() {
    private lateinit var adapter: SummaryAdapter
    private lateinit var timeframeSpinner: Spinner
    private lateinit var totalSmsTextView: TextView
    private lateinit var lastUpdatedTextView: TextView
    private lateinit var periodTextView: TextView
    private lateinit var summaryRecyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_summary)
        Log.d("Summary activity","initialising views")
        initializeViews()
        Log.d("Summary activity","initialising recycler")

        setupRecyclerView()
        Log.d("Summary activity","initialising spinner")

        setupTimeframeSpinner()
    }

    private fun initializeViews() {
        timeframeSpinner = findViewById(R.id.timeframeSpinner)
        totalSmsTextView = findViewById(R.id.totalSmsTextView)
        lastUpdatedTextView = findViewById(R.id.lastUpdatedTextView)
        periodTextView = findViewById(R.id.periodTextView)
        summaryRecyclerView = findViewById(R.id.summaryRecyclerView)
    }

    private fun setupRecyclerView() {
        adapter = SummaryAdapter()
        summaryRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@SummaryActivity)
            adapter = this@SummaryActivity.adapter
        }
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

            override fun onNothingSelected(parent: AdapterView<*>) {
                // Do nothing
            }
        }
    }

    private fun fetchSummary(timeframe: String) {
        lifecycleScope.launch {
            try {
                val userId = getUserId() // Implement this method to get the user ID
                val response = apiService.getUserSummary(userId, timeframe)
                if (response.isSuccessful) {
                    response.body()?.let { summary ->
                        displaySummary(summary)
                    }
                } else {
                    Toast.makeText(this@SummaryActivity, "Failed to fetch summary", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@SummaryActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun displaySummary(summary: UserSummary) {
        totalSmsTextView.text = "Total SMS: ${summary.totalSMS}"
        lastUpdatedTextView.text = "Last Updated: ${summary.lastUpdated}"
        periodTextView.text = "Period: ${summary.aggregate.period}"

        val categoryList = summary.aggregate.categoryAmounts.map { (category, amount) ->
            CategorySummary(category, amount)
        }
        adapter.submitList(categoryList)
    }

    private fun getUserId(): String {
        val sharedPrefs = getSharedPreferences("AppPrefs", MODE_PRIVATE)
        return sharedPrefs.getString("userId", "") ?: ""
    }
}