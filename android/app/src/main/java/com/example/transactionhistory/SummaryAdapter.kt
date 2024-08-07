package com.example.transactionhistory

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

class SummaryAdapter : ListAdapter<TransactionSummary, SummaryAdapter.ViewHolder>(SummaryDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_summary, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val summary = getItem(position)
        holder.bind(summary)
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val categoryTextView: TextView = itemView.findViewById(R.id.categoryTextView)
        private val amountTextView: TextView = itemView.findViewById(R.id.amountTextView)
        private val countTextView: TextView = itemView.findViewById(R.id.countTextView)

        fun bind(summary: TransactionSummary) {
            categoryTextView.text = summary.category
            amountTextView.text = "Total: $${summary.totalAmount}"
            countTextView.text = "Count: ${summary.transactionCount}"
        }
    }
}

class SummaryDiffCallback : DiffUtil.ItemCallback<TransactionSummary>() {
    override fun areItemsTheSame(oldItem: TransactionSummary, newItem: TransactionSummary): Boolean {
        return oldItem.category == newItem.category
    }

    override fun areContentsTheSame(oldItem: TransactionSummary, newItem: TransactionSummary): Boolean {
        return oldItem == newItem
    }
}