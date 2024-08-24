from androidx.compose.ui.platform import AndroidCompositionLocals_androidKt
from pycomposeui.runtime import Composable


_LocalContext = AndroidCompositionLocals_androidKt.getLocalContext()


class LocalContext:
    @property
    def current(self):
        return _LocalContext.getCurrent(Composable.composer, 1)


LocalContext = LocalContext()
