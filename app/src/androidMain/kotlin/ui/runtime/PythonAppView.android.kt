package ui.runtime

import android.util.Log
import androidx.compose.foundation.BorderStroke
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.currentComposer
import androidx.compose.runtime.internal.ComposableLambda
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.Dp
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform


private const val tag = "PythonAppView_androidKt"


@Composable
actual fun startPythonInterpreter() {
    try {
        if (!Python.isStarted()) {
            val platform = AndroidPlatform(LocalContext.current)
            platform.redirectStdioToLogcat()
            Python.start(platform)
            Log.i(tag, "Python interpreter is started.")
        } else {
            Log.i(tag, "Python interpreter is already started.")
        }
    } catch (e: Exception) {
        Log.e(tag, "Failed to start Python interpreter.")
        e.printStackTrace()
    }
}


private fun getPyModule(name: String): PyObject {
    if (!Python.isStarted()) throw IllegalStateException("Python is not started yet. Please run startPythonInterpreter() first.")
    return Python.getInstance().getModule(name)
}

val sys: PyObject
    get() = getPyModule("sys")
val version: String
    get() = sys["version"].toString()
val os: PyObject
    get() = getPyModule("os")


fun runPy(functionName: String, moduleName: String = moduleNamePreset, vararg args: Any): PyObject {
    val module = getPyModule(moduleName)
    return when {
        args.isEmpty() -> module.callAttr(functionName)
        else -> module.callAttr(functionName, *(args.toList().toTypedArray()))
    }
}


@Composable
actual fun PythonWidget(
    composableName: String,
    modifier: Modifier,
    shape: Shape,
    color: Color,
    contentColor: Color,
    tonalElevation: Dp,
    shadowElevation: Dp,
    border: BorderStroke?,
    moduleName: String,
    content: @Composable (args: Array<Any>) -> Unit
) {
    val module = getPyModule(moduleName)
    Surface(modifier, shape, color, contentColor, tonalElevation, shadowElevation, border) {
        module.callAttr(composableName, content)
    }
}


@Composable
actual fun PythonAppView(
    modifier: Modifier,
    shape: Shape,
    color: Color,
    contentColor: Color,
    tonalElevation: Dp,
    shadowElevation: Dp,
    border: BorderStroke?,
    moduleName: String,
    composableAppClassName: String,
    content: @Composable (args: Array<Any>) -> Unit
) {
    val module = getPyModule(moduleName)
    val appView = module.callAttr(composableAppClassName, currentComposer)
    Surface(modifier, shape, color, contentColor, tonalElevation, shadowElevation, border) {
        if (appView is ComposableLambda) {
            appView(currentComposer, 1)
        } else {
            Log.e(tag, "Failed to call $composableAppClassName.")
        }
    }
}
