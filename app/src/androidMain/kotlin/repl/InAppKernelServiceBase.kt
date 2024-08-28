package repl

import android.app.*
import android.util.Log
import android.os.IBinder
import android.content.Intent
import android.content.Context
import kotlin.system.exitProcess
import androidx.core.app.NotificationCompat

import com.chaquo.python.android.AndroidPlatform
import com.chaquo.python.Python


open class InAppKernelServiceBase : Service() {
    companion object {
        const val MAX_WORKERS = 10  // Maximum number of workers that can be run simultaneously (will be referenced in python code)
        const val NOTIFICATION_ID_PREFIX = 10000
        const val FOREGROUND_ERROR_MESSAGE = "" +
            "The REPL App should be in foreground when Python Kernel is trying to start" +
            " due to Android 10+ restrictions. Please let the app run in foreground and retry.\n" +
            "If you are using the app in foreground and still facing this issue, please report it.\n"
    }

    protected open val index = -1
    protected open val tag = "InAppKernelService"
        get() = "$field$index"
    private val notificationId
        get() = NOTIFICATION_ID_PREFIX + index
    private val notificationChannelId = "InAppKernelServiceNotificationChannel"
        get() = "$field$index"
    private val serviceName = "PyREPL Kernel Service"
        get() = "$field $index"
    private val processName = "Python Process for REPL Kernel"
        get() = "$field $index"
    protected open val replModule = "repl.kernel"
    protected open val replPrepareFunction = "prepare_kernel"
    protected open val replFunction = "start_kernel"
    protected open val replInterruptFunction = "interrupt_kernel"
    protected open val usingMultiProcess = true
    private var isRunning = false

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        try {
            val notification = createNotification()
            startForeground(notificationId, notification)
        } catch (e: ForegroundServiceStartNotAllowedException) {
            throw ForegroundServiceStartNotAllowedException(
                FOREGROUND_ERROR_MESSAGE + "\nError: ${e.message}"
            )
        }

        if (!Python.isStarted()) {
            val platform = AndroidPlatform(this@InAppKernelServiceBase)
            Python.start(platform)
            Log.i(tag, "$processName started")
        }

        val repl = Python.getInstance().getModule(replModule)
        val workdir = intent.getStringExtra("workdir")
        val filename = intent.getStringExtra("filename")
        val signum = intent.getLongExtra("signum", -1L)

        if (!isRunning && workdir != null && filename != null) {
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
                        Log.i(tag, "$processName exited normally")
                    } catch (e: Exception) {
                        Log.e(tag, "$processName exited abnormally", e)
                    } finally {
                        stopSelf()
                    }
                }
            }.start()
            isRunning = true

            Log.i(tag, "$serviceName started")
        } else if (signum != -1L) {
            object : Thread() {
                override fun run() {
                    try {
                        repl.callAttr(
                            replInterruptFunction,
                            signum
                        )
                        Log.i(tag, "Interrupt to $processName exited normally")
                    } catch (e: Exception) {
                        Log.e(tag, "Interrupt to $processName exited abnormally", e)
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
        isRunning = false
        if (usingMultiProcess) {
            exitProcess(0)
        }
    }
}
