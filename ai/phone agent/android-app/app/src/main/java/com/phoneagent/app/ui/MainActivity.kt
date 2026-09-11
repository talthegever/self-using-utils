package com.phoneagent.app.ui

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.phoneagent.app.action.ActionExecutor
import com.phoneagent.app.action.ExecutionResult
import com.phoneagent.app.databinding.ActivityMainBinding
import com.phoneagent.app.intent.IntentMapper
import com.phoneagent.app.network.BrainClient
import com.phoneagent.app.permissions.PermissionManager
import com.phoneagent.app.settings.SettingsStore
import com.phoneagent.app.speech.SpeechModule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * The whole v1 UI: type or speak a command, see heard -> understood -> did
 * in the log. See design.txt section 4 for the component breakdown this
 * wires together.
 */
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var settings: SettingsStore
    private lateinit var speech: SpeechModule
    private lateinit var executor: ActionExecutor

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        settings = SettingsStore(this)
        speech = SpeechModule(this)
        executor = ActionExecutor(applicationContext)

        binding.sendButton.setOnClickListener {
            Log.d(TAG, "sendButton clicked")
            val text = binding.commandInput.text.toString().trim()
            if (text.isNotEmpty()) {
                binding.commandInput.text.clear()
                handleCommand(text)
            } else {
                Log.d(TAG, "sendButton clicked with empty input, ignoring")
            }
        }

        binding.micButton.setOnClickListener { startVoiceInput() }
        binding.settingsButton.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        val missing = PermissionManager.missingPermissions(this)
        if (missing.isNotEmpty()) {
            permissionLauncher.launch(missing.toTypedArray())
        }
    }

    override fun onResume() {
        super.onResume()
        updateServerStatus()
    }

    override fun onDestroy() {
        super.onDestroy()
        speech.stop()
    }

    private fun updateServerStatus() {
        binding.serverStatusText.text = if (settings.isConfigured) {
            "Server: ${settings.serverHost}:${settings.serverPort}"
        } else {
            "Server not configured - open Settings"
        }
    }

    private fun startVoiceInput(retryCount: Int = 0) {
        speech.startListening(
            onResult = { text -> runOnUiThread { handleCommand(text, isVoiceInput = true, retryCount = retryCount) } },
            onError = { message -> runOnUiThread { appendLog("error: $message") } },
        )
    }

    private fun handleCommand(text: String, isVoiceInput: Boolean = false, retryCount: Int = 0) {
        appendLog("heard: $text")

        if (!settings.isConfigured) {
            appendLog("did: server not configured - open Settings first")
            return
        }

        Log.d(TAG, "calling brain server at ${settings.serverHost}:${settings.serverPort}")

        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                try {
                    val client = BrainClient(settings.serverHost, settings.serverPort)
                    val raw = client.parseIntent(text)
                    Log.d(TAG, "raw response: $raw")

                    val action = IntentMapper.fromJson(raw)
                    withContext(Dispatchers.Main) { appendLog("understood: $action") }

                    executor.execute(action)
                } catch (e: Exception) {
                    Log.e(TAG, "request failed", e)
                    ExecutionResult.Failure("couldn't reach the server (${e.message})")
                }
            }

            appendLog("did: ${result.message}")

            // Deterministic failure handling: don't just drop a command we
            // couldn't act on. Ask for clarification, and if the user was
            // speaking, re-open the mic so a hands-free retry doesn't need a
            // tap - matches the same fixed rule for every kind of Failure
            // (unrecognized intent, no matching app/contact, etc.).
            if (result is ExecutionResult.Failure) {
                appendLog("PhoneAgent: sorry, could you say that again?")
                // Bounded: an unreachable server or a persistently
                // unrecognized command must not re-trigger the mic forever.
                if (isVoiceInput && retryCount < MAX_VOICE_RETRIES) {
                    startVoiceInput(retryCount + 1)
                }
            }
        }
    }

    private fun appendLog(line: String) {
        Log.d(TAG, line)
        binding.logText.append("$line\n")
        binding.logScroll.post { binding.logScroll.fullScroll(View.FOCUS_DOWN) }
    }

    companion object {
        private const val TAG = "PhoneAgent"
        private const val MAX_VOICE_RETRIES = 2
    }
}
