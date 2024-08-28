

class CoroutineScope(Composable):
    def __init__(self, scope, launcher):
        super().__init__()
        self._scope = scope
        self._launcher = launcher

    def launch(self, block: callable):
        self._launcher(self._scope, block)


class RememberCoroutineScope(CoroutineScope):
    def __init__(self):
        super().__init__(
            scope=_runtime.rememberCoroutineScopeWrapper(self.composer, 1),
            launcher=_runtime_android.coroutineLauncherWrapper
        )

    def launch(self, block: callable):
        self._launcher(self._scope, block)


class DefaultCoroutineScope(CoroutineScope):
    def __init__(self):
        super().__init__(
            scope=_runtime.defaultCoroutineScopeWrapper(self.composer, 1),
            launcher=_runtime_android.coroutineLauncherWrapper
        )


class MainCoroutineScope(CoroutineScope):
    def __init__(self):
        super().__init__(
            scope=_runtime.mainCoroutineScopeWrapper(self.composer, 1),
            launcher=_runtime_android.coroutineLauncherWrapper
        )


class IOCoroutineScope(CoroutineScope):
    def __init__(self):
        super().__init__(
            scope=_runtime.ioCoroutineScopeWrapper(self.composer, 1),
            launcher=_runtime_android.coroutineLauncherWrapper
        )


class UncondifiedCoroutineScope(CoroutineScope):
    def __init__(self):
        super().__init__(
            scope=_runtime.uncondifiedCoroutineScopeWrapper(self.composer, 1),
            launcher=_runtime_android.coroutineLauncherWrapper
        )
