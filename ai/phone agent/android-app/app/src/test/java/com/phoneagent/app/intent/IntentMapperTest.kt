package com.phoneagent.app.intent

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class IntentMapperTest {

    @Test
    fun `open app maps correctly`() {
        val result = IntentMapper.fromJson("""{"intent":"OpenApp","slots":{"app_name":"spotify"}}""")
        assertTrue(result is ActionIntent.OpenApp)
        assertEquals("spotify", (result as ActionIntent.OpenApp).appName)
    }

    @Test
    fun `close app maps correctly`() {
        val result = IntentMapper.fromJson("""{"intent":"CloseApp","slots":{"app_name":"spotify"}}""")
        assertTrue(result is ActionIntent.CloseApp)
    }

    @Test
    fun `call with contact name maps correctly`() {
        val result = IntentMapper.fromJson("""{"intent":"Call","slots":{"contact_name":"mom"}}""")
        assertTrue(result is ActionIntent.Call)
        val call = result as ActionIntent.Call
        assertEquals("mom", call.contactName)
        assertNull(call.phoneNumber)
    }

    @Test
    fun `call with both contact and number is unknown`() {
        val result = IntentMapper.fromJson(
            """{"intent":"Call","slots":{"contact_name":"mom","phone_number":"12345"}}""",
        )
        assertEquals(ActionIntent.Unknown, result)
    }

    @Test
    fun `call with neither is unknown`() {
        val result = IntentMapper.fromJson("""{"intent":"Call","slots":{}}""")
        assertEquals(ActionIntent.Unknown, result)
    }

    @Test
    fun `calendar event with offset datetime maps correctly`() {
        val result = IntentMapper.fromJson(
            """{"intent":"CreateCalendarEvent","slots":{"title":"dentist","start_time":"2026-09-11T15:00:00+03:00"}}""",
        )
        assertTrue(result is ActionIntent.CreateCalendarEvent)
        assertNull((result as ActionIntent.CreateCalendarEvent).endTime)
    }

    @Test
    fun `calendar event with naive local datetime still parses`() {
        val result = IntentMapper.fromJson(
            """{"intent":"CreateCalendarEvent","slots":{"title":"dentist","start_time":"2026-09-11T15:00:00"}}""",
        )
        assertTrue(result is ActionIntent.CreateCalendarEvent)
    }

    @Test
    fun `reminder maps correctly`() {
        val result = IntentMapper.fromJson(
            """{"intent":"CreateReminder","slots":{"title":"take out trash","time":"2026-09-10T18:00:00"}}""",
        )
        assertTrue(result is ActionIntent.CreateReminder)
        assertEquals("take out trash", (result as ActionIntent.CreateReminder).title)
    }

    @Test
    fun `explicit unknown maps to unknown`() {
        val result = IntentMapper.fromJson("""{"intent":"Unknown","slots":{}}""")
        assertEquals(ActionIntent.Unknown, result)
    }

    @Test
    fun `missing required slot is unknown`() {
        val result = IntentMapper.fromJson("""{"intent":"OpenApp","slots":{}}""")
        assertEquals(ActionIntent.Unknown, result)
    }

    @Test
    fun `unrecognized intent name is unknown`() {
        val result = IntentMapper.fromJson("""{"intent":"DeleteEverything","slots":{}}""")
        assertEquals(ActionIntent.Unknown, result)
    }

    @Test
    fun `malformed json is unknown`() {
        val result = IntentMapper.fromJson("not json at all")
        assertEquals(ActionIntent.Unknown, result)
    }

    @Test
    fun `bad datetime is unknown`() {
        val result = IntentMapper.fromJson(
            """{"intent":"CreateReminder","slots":{"title":"x","time":"not-a-date"}}""",
        )
        assertEquals(ActionIntent.Unknown, result)
    }
}
