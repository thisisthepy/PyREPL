import os
import signal
import asyncio

from jupyter_server import auth
from jupyterlab.labapp import LabApp


from tornado.platform.asyncio import AnyThreadEventLoopPolicy


# Allow notebook to be run on a non-main thread.
asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
signal.signal = lambda signum, handler: signal.getsignal(signum)


class REPLConfigImpl:
    def __init__(self):
        self.LAB_ASSETS = os.path.join(os.path.dirname(__file__), "share", "jupyter", "lab")
        self.LAB_PW = "asdf1234"
        self.LAB_HOST = "0.0.0.0", 55555  # TODO: Implement a way to set this from the UI system
        self.LAB_URL = f"http://127.0.0.1:{self.LAB_HOST[1]}"  # TODO: Find a way to auto run a browser with this URL
        self.LAB_TOKEN = "asdf"  # TODO: Find a way to generate a random token in runtime
        self.LAB_SPACE = os.path.join(os.environ['HOME'], "lab")

    @property
    def LAB_CONFIG(self):
        return [
            f"--ip={self.LAB_HOST[0]}", f"--port={self.LAB_HOST[1]}",
            f"--app-dir={self.LAB_ASSETS}",  f"--notebook-dir={self.LAB_SPACE}",
            f"--IdentityProvider.token={self.LAB_TOKEN}",
            f"--PasswordIdentityProvider.hashed_password={auth.passwd(self.LAB_PW)}",
            "--MultiKernelManager.kernel_manager_class=repl.kernel.InAppKernelManager",
            "--ServerApp.allow_remote_access=True",
            "--no-browser"  # "--browser=chrome"
        ]


REPLConfig = REPLConfigImpl()


if not os.path.isdir(REPLConfig.LAB_SPACE):
    os.makedirs(REPLConfig.LAB_SPACE)
