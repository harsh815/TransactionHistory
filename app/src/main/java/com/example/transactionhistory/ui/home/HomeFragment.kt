package com.example.transactionhistory.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.example.transactionhistory.MainActivity
import com.example.transactionhistory.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val homeViewModel: HomeViewModel by viewModels()

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        val root: View = binding.root

        val textView: TextView = binding.textHome
        homeViewModel.text.observe(viewLifecycleOwner) {
            textView.text = it
        }
        return root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.readSmsButton.setOnClickListener {
            // Handle button click
            handleButtonClick()
        }
    }


    private fun handleButtonClick() {
        homeViewModel.onButtonClick()
        Toast.makeText(context, "Button clicked!", Toast.LENGTH_SHORT).show()
        (activity as MainActivity).readSms()
        homeViewModel.processingDone()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}