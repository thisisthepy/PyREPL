from androidx.compose.runtime.saveable import RememberSaveableKt

from pythonx.compose.runtime import Composable


@Composable
def remember_saveable(value):  # TODO: Add type hint and default value
    _type = type(value).__name__
    if _type == "int":
        if value < -2147483648 or value > 2147483647:
            _type = "long"
    return _rememberSaveable(value, _type, Composable.composer, 1)


