package com.phoneagent.app.action

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ExecutionResultTest {

    @Test
    fun `success carries its message`() {
        val result: ExecutionResult = ExecutionResult.Success("Opened Chrome.")
        assertTrue(result is ExecutionResult.Success)
        assertEquals("Opened Chrome.", result.message)
    }

    @Test
    fun `failure carries its message`() {
        val result: ExecutionResult = ExecutionResult.Failure("No installed app matches \"foo\".")
        assertTrue(result is ExecutionResult.Failure)
        assertEquals("No installed app matches \"foo\".", result.message)
    }
}
