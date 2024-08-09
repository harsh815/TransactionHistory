package com.example.transactionhistory

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

class SummaryAdapter : ListAdapter<Aggregate, SummaryAdapter.ViewHolder>(AggregateDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_summary, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val periodTextView: TextView = itemView.findViewById(R.id.periodTextView)
        private val totalSmsTextView: TextView = itemView.findViewById(R.id.totalSmsTextView)
        private val categoriesTextView: TextView = itemView.findViewById(R.id.categoriesTextView)

        fun bind(aggregate: Aggregate) {
            periodTextView.text = "Period: ${aggregate.period}"
            totalSmsTextView.text = "Total SMS: ${aggregate.totalSMS}"
            categoriesTextView.text = "Categories: ${aggregate.categoryCounts}"
        }
    }
}

class AggregateDiffCallback : DiffUtil.ItemCallback<Aggregate>() {
    override fun areItemsTheSame(oldItem: Aggregate, newItem: Aggregate): Boolean {
        return oldItem.period == newItem.period
    }

    override fun areContentsTheSame(oldItem: Aggregate, newItem: Aggregate): Boolean {
        return oldItem == newItem
    }
}