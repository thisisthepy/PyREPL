package ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import ui.runtime.PythonAppView
import ui.theme.AppTheme


@Preview
@Composable
fun App() {
    AppTheme {
        PythonAppView(Modifier.fillMaxSize())
    }
}
