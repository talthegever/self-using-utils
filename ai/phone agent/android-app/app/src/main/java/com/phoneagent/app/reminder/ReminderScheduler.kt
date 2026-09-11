package com.phoneagent.app.reminder

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import java.time.OffsetDateTime

class ReminderScheduler(private val context: Context) {

    /** Returns true if scheduled, false if the OS refused (e.g. exact-alarm
     * permission not granted on this Android version). */
    fun schedule(title: String, time: OffsetDateTime): Boolean {
        val alarmManager = context.getSystemService(AlarmManager::class.java)
        val triggerAtMillis = time.toInstant().toEpochMilli()
        val requestCode = title.hashCode()

        val intent = Intent(context, ReminderReceiver::class.java).apply {
            putExtra(ReminderReceiver.EXTRA_TITLE, title)
            putExtra(ReminderReceiver.EXTRA_ID, requestCode)
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            requestCode,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

        return try {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                pendingIntent,
            )
            true
        } catch (e: SecurityException) {
            false
        }
    }
}
