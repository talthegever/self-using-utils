package com.phoneagent.app.settings

import android.content.Context

/** Where the PC brain server lives on the LAN. See design.txt section 7/9. */
class SettingsStore(context: Context) {
    private val prefs = context.getSharedPreferences("phoneagent_settings", Context.MODE_PRIVATE)

    var serverHost: String
        get() = prefs.getString(KEY_HOST, "") ?: ""
        set(value) = prefs.edit().putString(KEY_HOST, value).apply()

    var serverPort: Int
        get() = prefs.getInt(KEY_PORT, DEFAULT_PORT)
        set(value) = prefs.edit().putInt(KEY_PORT, value).apply()

    val isConfigured: Boolean
        get() = serverHost.isNotBlank()

    companion object {
        private const val KEY_HOST = "server_host"
        private const val KEY_PORT = "server_port"
        const val DEFAULT_PORT = 8787
    }
}
