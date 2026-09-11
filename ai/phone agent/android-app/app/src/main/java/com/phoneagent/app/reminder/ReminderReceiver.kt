package com.phoneagent.app.reminder

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val title = intent.getStringExtra(EXTRA_TITLE) ?: return
        val id = intent.getIntExtra(EXTRA_ID, title.hashCode())
        NotificationHelper.show(context, id, title)
    }

    companion object {
        const val EXTRA_TITLE = "title"
        const val EXTRA_ID = "id"
    }
}
