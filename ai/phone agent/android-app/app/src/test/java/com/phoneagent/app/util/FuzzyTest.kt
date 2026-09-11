package com.phoneagent.app.util

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class FuzzyTest {

    @Test
    fun `distance is zero for identical strings`() {
        assertEquals(0, Fuzzy.distance("spotify", "spotify"))
    }

    @Test
    fun `distance is case insensitive`() {
        assertEquals(0, Fuzzy.distance("Spotify", "spotify"))
    }

    @Test
    fun `distance counts a single substitution`() {
        assertEquals(1, Fuzzy.distance("spotify", "spotifx"))
    }

    @Test
    fun `distance counts insertions and deletions`() {
        assertEquals(1, Fuzzy.distance("chrome", "chrom"))
        assertEquals(3, Fuzzy.distance("chrome", "chr"))
    }

    data class Named(val label: String)

    @Test
    fun `bestMatch returns exact match`() {
        val candidates = listOf(Named("Spotify"), Named("Chrome"), Named("Camera"))
        val result = Fuzzy.bestMatch("chrome", candidates) { it.label }
        assertEquals("Chrome", result?.label)
    }

    @Test
    fun `bestMatch returns substring match`() {
        val candidates = listOf(Named("Google Chrome"), Named("Firefox"))
        val result = Fuzzy.bestMatch("chrome", candidates) { it.label }
        assertEquals("Google Chrome", result?.label)
    }

    @Test
    fun `bestMatch tolerates small typos`() {
        val candidates = listOf(Named("Spotify"), Named("Camera"))
        val result = Fuzzy.bestMatch("spotifi", candidates) { it.label }
        assertEquals("Spotify", result?.label)
    }

    @Test
    fun `bestMatch returns null when nothing is close enough`() {
        val candidates = listOf(Named("Spotify"), Named("Camera"))
        val result = Fuzzy.bestMatch("zzzzzzzzzz", candidates) { it.label }
        assertNull(result)
    }

    @Test
    fun `bestMatch returns null for empty query`() {
        assertNull(Fuzzy.bestMatch("", listOf(Named("Spotify"))) { it.label })
    }

    @Test
    fun `bestMatch returns null for empty candidate list`() {
        assertNull(Fuzzy.bestMatch("spotify", emptyList<Named>()) { it.label })
    }
}
