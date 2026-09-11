package com.phoneagent.app.action

import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.CalendarContract
import com.phoneagent.app.accessibility.CloseAppAccessibilityService
import com.phoneagent.app.intent.ActionIntent
import com.phoneagent.app.reminder.ReminderScheduler
import com.phoneagent.app.resolver.AppResolver
import com.phoneagent.app.resolver.ContactResolver
import java.util.TimeZone

/**
 * The deterministic dispatcher described in design.txt section 3/4: exactly
 * one function per ActionIntent case, each calling a fixed Android API.
 * Nothing here is built dynamically from model output - by the time an
 * ActionIntent reaches this class it has already passed IntentMapper's
 * schema check.
 *
 * Call execute() from a background thread; several branches (CloseApp) block
 * briefly and none of them should run on the UI thread.
 */
class ActionExecutor(
    private val context: Context,
    private val appResolver: AppResolver = AppResolver(context),
    private val contactResolver: ContactResolver = ContactResolver(context),
    private val reminderScheduler: ReminderScheduler = ReminderScheduler(context),
) {
    fun execute(action: ActionIntent): ExecutionResult = try {
        when (action) {
            is ActionIntent.OpenApp -> openApp(action.appName)
            is ActionIntent.CloseApp -> closeApp(action.appName)
            is ActionIntent.Call -> call(action)
            is ActionIntent.CreateCalendarEvent -> createCalendarEvent(action)
            is ActionIntent.CreateReminder -> createReminder(action)
            ActionIntent.Unknown -> ExecutionResult.Failure("Didn't understand that command.")
        }
    } catch (e: SecurityException) {
        // A required runtime permission wasn't granted. This must surface as
        // its own Failure - letting it propagate would have MainActivity's
        // network try/catch misreport it as a server connectivity problem.
        ExecutionResult.Failure("Missing a required permission (${e.message}).")
    }

    private fun openApp(appName: String): ExecutionResult {
        val resolved = appResolver.resolve(appName)
            ?: return ExecutionResult.Failure("No installed app matches \"$appName\".")

        val launchIntent = context.packageManager.getLaunchIntentForPackage(resolved.packageName)
            ?: return ExecutionResult.Failure("${resolved.label} can't be launched.")

        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(launchIntent)
        return ExecutionResult.Success("Opened ${resolved.label}.")
    }

    private fun closeApp(appName: String): ExecutionResult {
        val service = CloseAppAccessibilityService.instance
            ?: return ExecutionResult.Failure(
                "Accessibility Service isn't enabled yet - enable PhoneAgent under Settings > Accessibility.",
            )
        val resolved = appResolver.resolve(appName)
            ?: return ExecutionResult.Failure("No installed app matches \"$appName\".")

        return if (service.closeApp(resolved.label)) {
            ExecutionResult.Success("Closed ${resolved.label}.")
        } else {
            ExecutionResult.Failure("Couldn't find ${resolved.label} in recent apps to close.")
        }
    }

    private fun call(action: ActionIntent.Call): ExecutionResult {
        val number = action.phoneNumber ?: action.contactName?.let { name ->
            contactResolver.resolve(name)?.phoneNumber
        }
        if (number == null) {
            val who = action.contactName ?: action.phoneNumber ?: "that contact"
            return ExecutionResult.Failure("Couldn't find a number for \"$who\".")
        }

        val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:$number")).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(dialIntent)
        return ExecutionResult.Success("Opened dialer for $number.")
    }

    private fun createCalendarEvent(action: ActionIntent.CreateCalendarEvent): ExecutionResult {
        val calendarId = defaultCalendarId()
            ?: return ExecutionResult.Failure("No calendar found to add the event to.")

        val endMillis = (action.endTime ?: action.startTime.plusHours(1))
            .toInstant().toEpochMilli()

        val values = ContentValues().apply {
            put(CalendarContract.Events.CALENDAR_ID, calendarId)
            put(CalendarContract.Events.TITLE, action.title)
            put(CalendarContract.Events.DTSTART, action.startTime.toInstant().toEpochMilli())
            put(CalendarContract.Events.DTEND, endMillis)
            put(CalendarContract.Events.EVENT_TIMEZONE, TimeZone.getDefault().id)
        }

        val uri = context.contentResolver.insert(CalendarContract.Events.CONTENT_URI, values)
            ?: return ExecutionResult.Failure("Couldn't create the calendar event.")

        return ExecutionResult.Success("Added \"${action.title}\" to your calendar (event $uri).")
    }

    private fun createReminder(action: ActionIntent.CreateReminder): ExecutionResult {
        return if (reminderScheduler.schedule(action.title, action.time)) {
            ExecutionResult.Success("Reminder set: \"${action.title}\" at ${action.time}.")
        } else {
            ExecutionResult.Failure("Couldn't schedule the reminder (exact-alarm permission missing?).")
        }
    }

    private fun defaultCalendarId(): Long? {
        val projection = arrayOf(CalendarContract.Calendars._ID)
        context.contentResolver.query(
            CalendarContract.Calendars.CONTENT_URI,
            projection,
            "${CalendarContract.Calendars.VISIBLE} = 1",
            null,
            null,
        )?.use { cursor ->
            if (cursor.moveToFirst()) {
                return cursor.getLong(cursor.getColumnIndexOrThrow(CalendarContract.Calendars._ID))
            }
        }
        return null
    }
}
