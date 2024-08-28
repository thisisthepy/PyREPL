from .config import REPLConfig
from .server import run_lab_server, send_server_launch_intent

import signal


_signal = signal.signal


# Override signal.signal to run the handler in the main scope
def setup_signal(scope):
    def custom_signal(sig, handler):
        def wrapper(signum, frame):
            scope.launch(lambda: handler(signum, frame))
        scope.launch(lambda: _signal(sig, wrapper))
    signal.signal = custom_signal


def disable_signal():
    signal.signal = lambda sig, handler: None
