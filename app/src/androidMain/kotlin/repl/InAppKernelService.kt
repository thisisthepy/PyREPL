@file:JvmName("InAppKernelService")

package repl

import android.R.drawable
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.chaquo.python.Python


class InAppKernelService : Service() {
    private val tag = "InAppKernelService"
    private val notificationChannelId = "InAppKernelServiceNotificationChannel"

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(1, notification)

        object : Thread() {
            override fun run() {
                try {
                    Python.getInstance()
                        .getModule("repl.kernel")
                        .callAttr(
                            "start_kernel",
                            intent.getStringExtra("workdir"),
                            intent.getStringExtra("filename")
                        )
                    Log.i(tag, "Python REPL Kernel exited normally")
                } catch (e: Exception) {
                    Log.e(tag, "Python REPL Kernel exited abnormally", e)
                } finally {
                    stopSelf()
                }
            }
        }.start()

        Log.i(tag, "Python REPL Kernel Service Started")
        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channel = NotificationChannel(
            notificationChannelId,
            "PyREPL Kernel Service",
            NotificationManager.IMPORTANCE_DEFAULT
        )
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.createNotificationChannel(channel)

        return NotificationCompat.Builder(this, notificationChannelId)
            .setContentTitle("Foreground Service")
            .setContentText("Service is running")
            .setSmallIcon(drawable.ic_secure)
            .build()
    }

    override fun onDestroy() {
        Log.i(tag, "Python REPL Kernel Service Destroyed")
        stopForeground(STOP_FOREGROUND_DETACH);
    }
}
