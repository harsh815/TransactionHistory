package com.example.transactionhistory

import android.Manifest
import android.content.pm.PackageManager
import android.icu.text.SimpleDateFormat
import android.os.Bundle
import android.view.Menu
import android.widget.Toast
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.navigation.NavigationView
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import androidx.drawerlayout.widget.DrawerLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.transactionhistory.databinding.ActivityMainBinding
import android.net.Uri;
import android.os.Handler
import org.json.JSONArray
import android.provider.Telephony
import org.json.JSONObject
import java.util.Date
import java.util.Locale


class MainActivity : AppCompatActivity() {

    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var binding: ActivityMainBinding

    companion object {
        private const val SMS_PERMISSION_CODE = 1
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.appBarMain.toolbar)

        binding.appBarMain.fab.setOnClickListener { view ->
            Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                .setAction("Action", null)
                .setAnchorView(R.id.fab).show()
        }
        val drawerLayout: DrawerLayout = binding.drawerLayout
        val navView: NavigationView = binding.navView
        val navController = findNavController(R.id.nav_host_fragment_content_main)
        // Passing each menu ID as a set of Ids because each
        // menu should be considered as top level destinations.
        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.nav_home, R.id.nav_gallery, R.id.nav_slideshow
            ), drawerLayout
        )
        setupActionBarWithNavController(navController, appBarConfiguration)
        navView.setupWithNavController(navController)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.main, menu)
        return true
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment_content_main)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }

    public fun readSms() {
        // Check for permission at runtime
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                arrayOf(Manifest.permission.READ_SMS),
                SMS_PERMISSION_CODE)
            return
        }
        val smsUri = Uri.parse("content://sms/inbox")
        val cursor = contentResolver.query(smsUri, null, null, null, null)
        val jsonArray = JSONArray()

        cursor?.use {
            while (cursor.moveToNext()) {
                val senderColumn = cursor.getColumnIndex(Telephony.Sms.ADDRESS)
                val dateColumn = cursor.getColumnIndex(Telephony.Sms.DATE)
                val bodyColumn = cursor.getColumnIndex(Telephony.Sms.BODY)

                val sender = cursor.getString(senderColumn)
                val timestamp = cursor.getLong(dateColumn)
                val content = cursor.getString(bodyColumn)

                val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ", Locale.getDefault())
                val formattedDate = sdf.format(Date(timestamp))

                val jsonObject = JSONObject().apply {
                    put("smsSender", sender)
                    put("timestamp", formattedDate)
                    put("smsContent", content)
                }

                jsonArray.put(jsonObject)
            }
        }
        Toast.makeText(applicationContext,jsonArray.toString(), Toast.LENGTH_SHORT).show()
    }
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == SMS_PERMISSION_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(applicationContext,"granted", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(applicationContext,"denied", Toast.LENGTH_SHORT).show()
            }
        }
    }
}