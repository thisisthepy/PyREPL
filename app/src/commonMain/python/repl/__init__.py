import os
import time
import signal

from jupyter_server import auth
from jupyter_server.auth.identity import IdentityProvider
from jupyterlab.labapp import LabApp

from .host import get_private_ip
from . import kernel


_signal = signal.signal


# Override signal.signal to run the handler in the main scope
def setup_signal(scope):
    def custom_signal(sig, handler):
        def wrapper(signum, frame):
            scope.launch(lambda: handler(signum, frame))
        scope.launch(lambda: _signal(sig, wrapper))
    signal.signal = custom_signal


class REPLConfig:
    @staticmethod
    def clean_directory(target_directory):
        # Get the current time
        current_time = time.time()

        # Iterate through all files in the target directory
        for filename in os.listdir(target_directory):
            file_path = os.path.join(target_directory, filename)

            # Check if it is a file
            if os.path.isfile(file_path):
                # Get the file's creation time
                creation_time = os.path.getctime(file_path)

                # Check if the file is older than 3 days (3 days * 24 hours * 60 minutes * 60 seconds)
                if (current_time - creation_time) > (3 * 24 * 60 * 60):
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted {file_path}")

    def __init__(self, kernel_manager=kernel.InAppKernelManager):
        self.LAB_ASSETS = os.path.join(os.path.dirname(__file__), "share", "jupyter", "lab")
        self.LAB_PW = "password"
        self.LAB_HOST = get_private_ip(), 55555
        self.LAB_TOKEN = IdentityProvider.token
        self.LAB_URL = f"http://{self.LAB_HOST[0]}:{self.LAB_HOST[1]}/lab?token={self.LAB_TOKEN}"
        self.LAB_SPACE = os.path.join(os.environ['HOME'], "lab")
        self._kernel_manager = kernel_manager
        self.KERNEL_MANAGER = kernel_manager.__module__ + "." + kernel_manager.__name__

        if not os.path.isdir(self.LAB_SPACE):
            os.makedirs(self.LAB_SPACE)

        runtime_dir = os.path.join(os.environ['HOME'], ".local", "share", "jupyter", "runtime")
        workspace_dir = os.path.join(os.environ['HOME'], ".jupyter", "lab", "workspaces")
        self.clean_directory(runtime_dir)
        self.clean_directory(workspace_dir)

    @property
    def ip(self):
        return self.LAB_HOST[0]

    @ip.setter
    def ip(self, value):
        self.LAB_HOST = (value, self.LAB_HOST[1])

    @property
    def port(self):
        return self.LAB_HOST[1]

    @port.setter
    def port(self, value):
        self.LAB_HOST = (self.LAB_HOST[0], value)

    @property
    def password(self):
        return self.LAB_PW

    @password.setter
    def password(self, value):
        self.LAB_PW = value

    @property
    def uri(self):
        return self.LAB_URL

    @property
    def list(self):
        return [
            f"--ip={self.LAB_HOST[0]}", f"--port={self.LAB_HOST[1]}",
            f"--app-dir={self.LAB_ASSETS}",  f"--notebook-dir={self.LAB_SPACE}",
            f"--IdentityProvider.token={self.LAB_TOKEN}",
            f"--PasswordIdentityProvider.hashed_password={auth.passwd(self.LAB_PW)}",
            f"--MultiKernelManager.kernel_manager_class={self.KERNEL_MANAGER}",
            "--ServerApp.allow_remote_access=True",
            "--no-browser"
        ]
