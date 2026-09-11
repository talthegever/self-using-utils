package com.phoneagent.app.resolver

import android.content.Context
import android.provider.ContactsContract
import com.phoneagent.app.util.Fuzzy

data class ResolvedContact(val displayName: String, val phoneNumber: String)

/** Resolves a spoken contact name to a phone number via ContactsContract.
 * Requires READ_CONTACTS (see AndroidManifest.xml / PermissionManager). */
class ContactResolver(private val context: Context) {

    fun resolve(name: String): ResolvedContact? {
        val contacts = queryContacts()
        return Fuzzy.bestMatch(name, contacts) { it.displayName }
    }

    private fun queryContacts(): List<ResolvedContact> {
        val results = mutableListOf<ResolvedContact>()
        val projection = arrayOf(
            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
            ContactsContract.CommonDataKinds.Phone.NUMBER,
        )
        context.contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            projection,
            null,
            null,
            null,
        )?.use { cursor ->
            val nameIdx = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
            val numberIdx = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
            while (cursor.moveToNext()) {
                val name = cursor.getString(nameIdx) ?: continue
                val number = cursor.getString(numberIdx) ?: continue
                results.add(ResolvedContact(name, number))
            }
        }
        return results
    }
}
