package com.phoneagent.app.intent

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertSame
import org.junit.Test
import java.time.OffsetDateTime

class ActionIntentTest {

    @Test
    fun `equal data classes with same fields are equal`() {
        assertEquals(ActionIntent.OpenApp("spotify"), ActionIntent.OpenApp("spotify"))
        assertNotEquals(ActionIntent.OpenApp("spotify"), ActionIntent.OpenApp("chrome"))
    }

    @Test
    fun `different intent types are never equal even with similar fields`() {
        val openApp: ActionIntent = ActionIntent.OpenApp("spotify")
        val closeApp: ActionIntent = ActionIntent.CloseApp("spotify")
        assertNotEquals(openApp, closeApp)
    }

    @Test
    fun `call intent equality considers both slots`() {
        assertEquals(ActionIntent.Call("mom", null), ActionIntent.Call("mom", null))
        assertNotEquals(ActionIntent.Call("mom", null), ActionIntent.Call(null, "555"))
    }

    @Test
    fun `unknown is a singleton`() {
        assertSame(ActionIntent.Unknown, ActionIntent.Unknown)
    }

    @Test
    fun `calendar event equality considers optional end time`() {
        val start = OffsetDateTime.parse("2026-09-11T15:00:00+03:00")
        val a = ActionIntent.CreateCalendarEvent("dentist", start, null)
        val b = ActionIntent.CreateCalendarEvent("dentist", start, null)
        val c = ActionIntent.CreateCalendarEvent("dentist", start, start.plusHours(1))
        assertEquals(a, b)
        assertNotEquals(a, c)
    }

    @Test
    fun `reminder equality considers time`() {
        val t1 = OffsetDateTime.parse("2026-09-10T18:00:00+03:00")
        val t2 = OffsetDateTime.parse("2026-09-10T19:00:00+03:00")
        assertEquals(ActionIntent.CreateReminder("trash", t1), ActionIntent.CreateReminder("trash", t1))
        assertNotEquals(ActionIntent.CreateReminder("trash", t1), ActionIntent.CreateReminder("trash", t2))
    }
}
