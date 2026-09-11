package com.phoneagent.app.util

/** Small Levenshtein-distance based matcher, used to resolve a spoken app
 * or contact name against what's actually on the device. */
object Fuzzy {
    fun distance(a: String, b: String): Int {
        val s = a.lowercase()
        val t = b.lowercase()
        val dp = Array(s.length + 1) { IntArray(t.length + 1) }
        for (i in 0..s.length) dp[i][0] = i
        for (j in 0..t.length) dp[0][j] = j
        for (i in 1..s.length) {
            for (j in 1..t.length) {
                val cost = if (s[i - 1] == t[j - 1]) 0 else 1
                dp[i][j] = minOf(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost,
                )
            }
        }
        return dp[s.length][t.length]
    }

    /**
     * Returns the best match from [candidates] for [query] using label text,
     * or null if nothing is close enough. Exact/substring matches always win;
     * otherwise the edit distance must be small relative to the query length.
     */
    fun <T> bestMatch(query: String, candidates: List<T>, label: (T) -> String): T? {
        val q = query.trim().lowercase()
        if (q.isEmpty() || candidates.isEmpty()) return null

        candidates.firstOrNull { label(it).lowercase() == q }?.let { return it }
        candidates.firstOrNull { label(it).lowercase().contains(q) }?.let { return it }

        val threshold = (q.length / 3).coerceAtLeast(1)
        return candidates
            .map { it to distance(q, label(it)) }
            .minByOrNull { it.second }
            ?.takeIf { it.second <= threshold }
            ?.first
    }
}
