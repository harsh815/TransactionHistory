package com.example.transactionhistory.ui.home

import android.os.Handler
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class HomeViewModel : ViewModel() {

    private val _text = MutableLiveData<String>().apply {
        value = "Click to analyse SMS data"
    }
    val text: LiveData<String> = _text

    fun onButtonClick() {
        _text.value = "Analyzing SMS data..."
    }

    fun processingDone() {
         Handler().postDelayed({_text.value = "finished"}, 5000)
    }
}