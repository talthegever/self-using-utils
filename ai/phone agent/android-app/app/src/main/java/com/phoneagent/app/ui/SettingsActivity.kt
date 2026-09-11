package com.phoneagent.app.ui

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.phoneagent.app.databinding.ActivitySettingsBinding
import com.phoneagent.app.settings.SettingsStore

class SettingsActivity : AppCompatActivity() {
    private lateinit var binding: ActivitySettingsBinding
    private lateinit var settings: SettingsStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        settings = SettingsStore(this)

        binding.hostInput.setText(settings.serverHost)
        binding.portInput.setText(settings.serverPort.toString())

        binding.saveButton.setOnClickListener {
            settings.serverHost = binding.hostInput.text.toString().trim()
            settings.serverPort =
                binding.portInput.text.toString().toIntOrNull() ?: SettingsStore.DEFAULT_PORT
            finish()
        }
    }
}
