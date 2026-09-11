package com.phoneagent.app.resolver

import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import com.phoneagent.app.util.Fuzzy

data class ResolvedApp(val packageName: String, val label: String)

/** Resolves a spoken app name against what's actually installed. Deterministic
 * once a match is picked - the model never sees or chooses a package name. */
class AppResolver(private val context: Context) {

    fun resolve(appName: String): ResolvedApp? {
        val launchable = launchableApps(context.packageManager)
        return Fuzzy.bestMatch(appName, launchable) { it.label }
    }

    private fun launchableApps(pm: PackageManager): List<ResolvedApp> {
        val flags = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            PackageManager.ApplicationInfoFlags.of(0)
        } else null

        @Suppress("DEPRECATION")
        val apps: List<ApplicationInfo> = if (flags != null) {
            pm.getInstalledApplications(flags)
        } else {
            pm.getInstalledApplications(0)
        }

        return apps.mapNotNull { info ->
            val launchIntent: Intent? = pm.getLaunchIntentForPackage(info.packageName)
            if (launchIntent == null) {
                null
            } else {
                ResolvedApp(info.packageName, pm.getApplicationLabel(info).toString())
            }
        }
    }
}
