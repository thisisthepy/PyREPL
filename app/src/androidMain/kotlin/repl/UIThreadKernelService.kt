package repl

import android.widget.Toast
import android.content.Intent
import kotlin.system.exitProcess


class UIThreadKernelService: InAppKernelServiceBase() {
    override val index = NOTIFICATION_ID_PREFIX + MAX_WORKERS + 1
    override val usingMultiProcess = false

    override fun onDestroy() {
        super.onDestroy()

        Toast.makeText(this, "Restarting app...", Toast.LENGTH_SHORT).show()

        val intent = packageManager.getLaunchIntentForPackage(packageName)
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
            startActivity(intent)
        }

        exitProcess(0)
    }
}
