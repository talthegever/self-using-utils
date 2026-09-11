package com.phoneagent.app.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.graphics.Rect
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * Implements CloseApp (design.txt section 5): Android does not let a normal
 * app force-stop another app without root, so this opens the Recents screen
 * and dismisses the card matching the requested app's label.
 *
 * Must be enabled manually once under Settings > Accessibility (Android does
 * not allow silent self-enrollment) - see design.txt section 9. Recents UI
 * varies by OEM/launcher, so this first-pass matching/dismiss logic is
 * expected to need tuning once we can test it on the real device.
 *
 * Call closeApp() from a background thread - it blocks briefly waiting for
 * the Recents UI to render and for the dismiss gesture to complete.
 */
class CloseAppAccessibilityService : AccessibilityService() {

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) = Unit

    override fun onInterrupt() = Unit

    fun closeApp(appLabel: String): Boolean {
        performGlobalAction(GLOBAL_ACTION_RECENTS)
        Thread.sleep(RECENTS_RENDER_DELAY_MS)

        val root = rootInActiveWindow ?: return false
        val node = findNodeByLabel(root, appLabel) ?: return false
        return dismissNode(node)
    }

    private fun findNodeByLabel(node: AccessibilityNodeInfo, label: String): AccessibilityNodeInfo? {
        val text = node.text?.toString() ?: node.contentDescription?.toString()
        if (text != null && text.contains(label, ignoreCase = true)) {
            return node
        }
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            findNodeByLabel(child, label)?.let { return it }
        }
        return null
    }

    private fun dismissNode(node: AccessibilityNodeInfo): Boolean {
        val supportsDismiss = node.actionList.any { it.id == AccessibilityNodeInfo.ACTION_DISMISS }
        if (supportsDismiss) {
            return node.performAction(AccessibilityNodeInfo.ACTION_DISMISS)
        }
        val bounds = Rect()
        node.getBoundsInScreen(bounds)
        return dispatchSwipeUp(bounds)
    }

    private fun dispatchSwipeUp(bounds: Rect): Boolean {
        val path = Path().apply {
            moveTo(bounds.centerX().toFloat(), bounds.centerY().toFloat())
            lineTo(bounds.centerX().toFloat(), (bounds.top - SWIPE_DISTANCE_PX).toFloat())
        }
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, SWIPE_DURATION_MS))
            .build()

        val latch = CountDownLatch(1)
        var result = false
        dispatchGesture(
            gesture,
            object : GestureResultCallback() {
                override fun onCompleted(gestureDescription: GestureDescription?) {
                    result = true
                    latch.countDown()
                }

                override fun onCancelled(gestureDescription: GestureDescription?) {
                    latch.countDown()
                }
            },
            null,
        )
        latch.await(GESTURE_TIMEOUT_SEC, TimeUnit.SECONDS)
        return result
    }

    companion object {
        var instance: CloseAppAccessibilityService? = null
            private set

        private const val RECENTS_RENDER_DELAY_MS = 400L
        private const val SWIPE_DISTANCE_PX = 200
        private const val SWIPE_DURATION_MS = 300L
        private const val GESTURE_TIMEOUT_SEC = 1L
    }
}
