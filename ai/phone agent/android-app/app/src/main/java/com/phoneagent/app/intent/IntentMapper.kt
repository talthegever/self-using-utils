package com.phoneagent.app.intent

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeParseException

/**
 * Maps the brain server's raw JSON response onto [ActionIntent].
 *
 * This is the phone-side half of the "belt and suspenders" validation from
 * design.txt section 6: the server already validates against the schema
 * with Pydantic, but the phone never trusts that blindly - anything that
 * doesn't cleanly fit one of the known shapes here becomes Unknown too.
 */
object IntentMapper {
    private val json = Json { ignoreUnknownKeys = true }

    @Serializable
    private data class RawResponse(val intent: String, val slots: JsonObject)

    fun fromJson(raw: String): ActionIntent {
        val response = try {
            json.decodeFromString(RawResponse.serializer(), raw)
        } catch (e: Exception) {
            return ActionIntent.Unknown
        }
        return try {
            mapSlots(response.intent, response.slots)
        } catch (e: Exception) {
            ActionIntent.Unknown
        }
    }

    private fun mapSlots(intent: String, slots: JsonObject): ActionIntent = when (intent) {
        "OpenApp" -> ActionIntent.OpenApp(requireString(slots, "app_name"))
        "CloseApp" -> ActionIntent.CloseApp(requireString(slots, "app_name"))
        "Call" -> {
            val contact = optionalString(slots, "contact_name")
            val phone = optionalString(slots, "phone_number")
            if ((contact != null) == (phone != null)) {
                ActionIntent.Unknown
            } else {
                ActionIntent.Call(contact, phone)
            }
        }
        "CreateCalendarEvent" -> ActionIntent.CreateCalendarEvent(
            title = requireString(slots, "title"),
            startTime = requireDateTime(slots, "start_time"),
            endTime = optionalDateTime(slots, "end_time"),
        )
        "CreateReminder" -> ActionIntent.CreateReminder(
            title = requireString(slots, "title"),
            time = requireDateTime(slots, "time"),
        )
        else -> ActionIntent.Unknown
    }

    private fun requireString(obj: JsonObject, key: String): String =
        optionalString(obj, key) ?: throw IllegalArgumentException("missing $key")

    private fun optionalString(obj: JsonObject, key: String): String? =
        (obj[key] as? JsonPrimitive)?.takeIf { it.isString }?.content?.takeIf { it.isNotBlank() }

    private fun requireDateTime(obj: JsonObject, key: String): OffsetDateTime =
        parseDateTime(requireString(obj, key)) ?: throw IllegalArgumentException("bad datetime $key")

    private fun optionalDateTime(obj: JsonObject, key: String): OffsetDateTime? =
        optionalString(obj, key)?.let { parseDateTime(it) }

    private fun parseDateTime(text: String): OffsetDateTime? = try {
        OffsetDateTime.parse(text)
    } catch (e: DateTimeParseException) {
        try {
            LocalDateTime.parse(text).atZone(ZoneId.systemDefault()).toOffsetDateTime()
        } catch (e2: DateTimeParseException) {
            null
        }
    }
}
