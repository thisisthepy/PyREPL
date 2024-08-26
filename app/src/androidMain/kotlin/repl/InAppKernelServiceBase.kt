@file:JvmName("InAppKernelServiceBase")

package repl

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlin.system.exitProcess


open class InAppKernelServiceBase : Service() {
    companion object {
        const val maxWorkers = 10  // Maximum number of workers that can be run simultaneously (will be referenced in python code)
    }

    protected open val index = -1
    protected open val tag = "InAppKernelService"
        get() = "$field$index"
    private val notificationId
        get() = 10000 + index
    private val notificationChannelId = "InAppKernelServiceNotificationChannel"
        get() = "$field$index"
    private val serviceName = "PyREPL Kernel Service"
        get() = "$field $index"
    protected open val replModule = "repl.kernel"
    protected open val replPrepareFunction = "prepare_kernel"
    protected open val replFunction = "start_kernel"
    protected open val replInterruptFunction = "interrupt_kernel"
    private var running = false

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        try {
            val notification = createNotification()
            startForeground(notificationId, notification)
        } catch (e: ForegroundServiceStartNotAllowedException) {
            throw ForegroundServiceStartNotAllowedException(
                "The REPL App should be in foreground when Python Kernel is trying to start" +
                " due to Android 10+ restrictions. Please let the app run in foreground and retry.\n" +
                "If you are using the app in foreground and still facing this issue, please report it.\n\n" +
                "Error: ${e.message}"
            )
        }

        if (!Python.isStarted()) {
            val platform = AndroidPlatform(this@InAppKernelServiceBase)
            Python.start(platform)
            Log.i(tag, "Python Process for REPL Kernel $index Started")
        }

        val repl = Python.getInstance().getModule(replModule)
        val workdir = intent.getStringExtra("workdir")
        val filename = intent.getStringExtra("filename")
        val signum = intent.getLongExtra("signum", -1L)

        if (!running && workdir != null && filename != null) {
            try {
                repl.callAttr(replPrepareFunction)
            } catch (e: Exception) {
                Log.e(tag, e.toString())
            }
            object : Thread() {
                override fun run() {
                    try {
                        repl.callAttr(
                            replFunction,
                            workdir,
                            filename
                        )
                        Log.i(tag, "Python REPL Kernel $index exited normally")
                    } catch (e: Exception) {
                        Log.e(tag, "Python REPL Kernel $index exited abnormally", e)
                    } finally {
                        stopSelf()
                    }
                }
            }.start()
            running = true

            Log.i(tag, "$serviceName Started")
        } else if (signum != -1L) {
            object : Thread() {
                override fun run() {
                    try {
                        repl.callAttr(
                            replInterruptFunction,
                            signum
                        )
                        Log.i(tag, "Interrupt Python REPL Kernel $index exited normally")
                    } catch (e: Exception) {
                        Log.e(tag, "Interrupt for Python REPL Kernel $index exited abnormally", e)
                    } finally {
                        stopSelf()
                    }
                }
            }.start()

            Log.i(tag, "$serviceName Interrupted")
        } else {
            Log.i(tag, "$serviceName Already Running")
        }

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
            .setContentTitle(serviceName)
            .setContentText("Service is running")
            .build()
    }

    override fun onDestroy() {
        Log.i(tag, "$serviceName Destroyed")
        stopForeground(STOP_FOREGROUND_DETACH)
        running = false
        exitProcess(0)
    }
}
