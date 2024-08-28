package repl

import android.app.*
import android.util.Log
import android.os.IBinder
import android.widget.Toast
import android.content.Intent
import android.content.Context
import kotlin.system.exitProcess
import androidx.core.app.NotificationCompat
import repl.InAppKernelServiceBase.Companion.FOREGROUND_ERROR_MESSAGE

import com.chaquo.python.android.AndroidPlatform
import com.chaquo.python.Python


open class InAppLabServerService : Service() {
    protected open val tag = "InAppLabServerService"
    private val notificationId = InAppKernelServiceBase.NOTIFICATION_ID_PREFIX - 2
    private val notificationChannelId = "InAppLabServerServiceNotificationChannel"
    private val serviceName = "PyREPL Lab Server Service"
    private val processName = "Python Process for REPL Lab Server"
    protected open val replModule = "repl"
    protected open val replSignalHandler = "disable_signal"
    protected open val replLauncher = "run_lab_server"
    private var isRunning = false

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        if (isRunning) {
            Log.i(tag, "$serviceName already running")
            return START_NOT_STICKY
        }

        try {
            val notification = createNotification()
            startForeground(notificationId, notification)
        } catch (e: ForegroundServiceStartNotAllowedException) {
            val message = FOREGROUND_ERROR_MESSAGE + "\nError: ${e.message}"
            Toast.makeText(applicationContext, message, Toast.LENGTH_LONG).show()
            throw ForegroundServiceStartNotAllowedException(message)
        }

        if (!Python.isStarted()) {
            val platform = AndroidPlatform(this@InAppLabServerService)
            platform.redirectStdioToLogcat()
            Python.start(platform)
            Log.i(tag, "$processName started")
        }

        val repl = Python.getInstance().getModule(replModule)
        val ip = intent.getStringExtra("ip")
        val port = intent.getLongExtra("port", 55555L)
        val password = intent.getStringExtra("password")
        val manager = intent.getStringExtra("manager")

        object : Thread() {
            override fun run() {
                try {
                    repl.callAttr(replSignalHandler)
                    repl.callAttr(
                        replLauncher,
                        ip,
                        port,
                        password,
                        manager
                    )
                    Log.i(tag, "$processName exited normally")
                } catch (e: Exception) {
                    Log.e(tag, "$processName exited abnormally", e)
                    Toast.makeText(
                        applicationContext,
                        "An Error occurred in $processName: ${e.message}",
                        Toast.LENGTH_LONG
                    ).show()
                } finally {
                    stopSelf()
                }
            }
        }.start()
        isRunning = true

        Log.i(tag, "$serviceName started")

        return START_NOT_STICKY
    }

    private fun createNotification(): Notification {
        val channel = NotificationChannel(
            notificationChannelId,
            "PyREPL Lab Server Service",
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
        exitProcess(0)
    }
}
