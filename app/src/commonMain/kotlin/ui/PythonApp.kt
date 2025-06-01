package ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Surface
import androidx.compose.material3.VerticalDivider
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import io.github.thisisthepy.pycomposeui.PythonAppView
import io.github.thisisthepy.pycomposeui.PythonLauncher
import ui.theme.AppTheme


@Preview
@Composable
fun App() {
    AppTheme {
        PythonLauncher {
            BoxWithConstraints {
                val isLandscape = maxWidth > maxHeight

                if (isLandscape) {
                    // Landscape mode
                    Row(
                        modifier = Modifier.fillMaxSize().systemBarsPadding()
                    ) {
                        PythonAppView(Modifier.fillMaxSize().padding(16.dp))
                        VerticalDivider(modifier = Modifier.fillMaxHeight(), thickness = 0.2.dp)
                    }
                } else {
                    // Portrait mode
                    Column(
                        modifier = Modifier.fillMaxSize().systemBarsPadding().padding(2.dp)
                    ) {
                        PythonAppView(Modifier.fillMaxSize().padding(16.dp))
                    }
                }
            }
        }
    }
}
