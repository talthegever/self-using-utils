package com.phoneagent.app.intent

import java.time.OffsetDateTime

/**
 * The fixed, deterministic action set from design.txt section 5/6. This is
 * a sealed class on purpose: the Kotlin compiler forces every dispatch site
 * (see ActionExecutor) to handle every case, so there is no way to add a
 * freeform/dynamic action without a compile error.
 */
sealed class ActionIntent {
    data class OpenApp(val appName: String) : ActionIntent()
    data class CloseApp(val appName: String) : ActionIntent()
    data class Call(val contactName: String?, val phoneNumber: String?) : ActionIntent()
    data class CreateCalendarEvent(
        val title: String,
        val startTime: OffsetDateTime,
        val endTime: OffsetDateTime?,
    ) : ActionIntent()
    data class CreateReminder(val title: String, val time: OffsetDateTime) : ActionIntent()
    data object Unknown : ActionIntent()
}
