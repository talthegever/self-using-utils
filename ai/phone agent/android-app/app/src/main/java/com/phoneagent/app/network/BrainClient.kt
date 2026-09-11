package com.phoneagent.app.network

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Talks to the PC brain server's single endpoint. This class only moves
 * text back and forth - it never interprets the response. IntentMapper does
 * that, deterministically, once this returns.
 */
class BrainClient(private val host: String, private val port: Int) {

    /** Returns the server's raw JSON response body, or throws IOException. */
    fun parseIntent(text: String): String {
        val url = "http://$host:$port/parse-intent"
        val body = json.encodeToString(ParseRequest.serializer(), ParseRequest(text))
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder().url(url).post(body).build()

        sharedClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("brain server returned ${response.code}")
            }
            return response.body?.string() ?: throw IOException("empty response body")
        }
    }

    @Serializable
    private data class ParseRequest(val text: String)

    companion object {
        // OkHttpClient owns its own connection/thread pools and is meant to
        // be a shared singleton - a fresh one per request (MainActivity
        // builds a new BrainClient per command) would spin up new pools
        // every time and lose connection reuse.
        private val sharedClient = OkHttpClient.Builder()
            .connectTimeout(5, TimeUnit.SECONDS)
            // Local LLM inference on modest hardware can be slow, especially
            // the first call after the model was just loaded (cold start can
            // take well over a minute). Subsequent calls are much faster
            // since Ollama keeps the model warm in memory for a while.
            .readTimeout(120, TimeUnit.SECONDS)
            .build()

        private val json = Json { ignoreUnknownKeys = true }
    }
}
