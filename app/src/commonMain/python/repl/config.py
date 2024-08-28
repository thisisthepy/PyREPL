import os
import time

from jupyter_server import auth
from jupyter_server.auth.identity import IdentityProvider

from .host import get_private_ip
from . import kernel


class REPLConfig:
    RUNTIME_DIR = os.path.join(os.environ['HOME'], ".local", "share", "jupyter", "runtime")
    WORKSPACE_DIR = os.path.join(os.environ['HOME'], ".jupyter", "lab", "workspaces")

    LAB_ASSETS = os.path.join(os.path.dirname(__file__), "share", "jupyter", "lab")
    LAB_SPACE = os.path.join(os.environ['HOME'], "lab")

    @staticmethod
    def clean_directory(target_directory):
        # Get the current time
        current_time = time.time()

        if not os.path.isdir(target_directory):
            return

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

    def __init__(
            self,
            ip=get_private_ip(),
            port=55555,
            password="password",
            token=IdentityProvider.token,
            manager_class=kernel.InAppKernelManager,
            cache_clean=False
        ):
        self._LAB_PW = password
        self._LAB_HOST = ip, port
        self._LAB_TOKEN = token
        self._KERNEL_MANAGER = manager_class.__module__ + "." + manager_class.__name__

        if not os.path.isdir(self.LAB_SPACE):
            os.makedirs(self.LAB_SPACE)

        if cache_clean:
            self.clean_directory(self.RUNTIME_DIR)
            self.clean_directory(self.WORKSPACE_DIR)

    @property
    def ip(self):
        return self._LAB_HOST[0]

    @ip.setter
    def ip(self, value):
        self._LAB_HOST = (value, self._LAB_HOST[1])

    @property
    def port(self):
        return self._LAB_HOST[1]

    @port.setter
    def port(self, value):
        self._LAB_HOST = (self._LAB_HOST[0], value)

    @property
    def password(self):
        return self._LAB_PW

    @password.setter
    def password(self, value):
        self._LAB_PW = value

    @property
    def manager(self):
        return self._KERNEL_MANAGER

    @manager.setter
    def manager(self, value):
        if isinstance(value, str):
            self._KERNEL_MANAGER = value
        else:
            self._KERNEL_MANAGER = value.__module__ + "." + value.__name__

    @property
    def uri(self):
        return f"http://{self._LAB_HOST[0]}:{self._LAB_HOST[1]}/lab?token={self._LAB_TOKEN}"

    @property
    def dict(self):
        return {
            "ip": self._LAB_HOST[0],
            "port": self._LAB_HOST[1],
            "password": self._LAB_PW,
            "token": str(self._LAB_TOKEN),
            "manager": self._KERNEL_MANAGER
        }

    @property
    def list(self):
        return [
            f"--ip={self._LAB_HOST[0]}", f"--port={self._LAB_HOST[1]}",
            f"--app-dir={self.LAB_ASSETS}",  f"--notebook-dir={self.LAB_SPACE}",
            f"--IdentityProvider.token={self._LAB_TOKEN}",  # Token is automatically disabled when password is set
            f"--PasswordIdentityProvider.hashed_password={auth.passwd(self._LAB_PW)}",
            f"--MultiKernelManager.kernel_manager_class={self._KERNEL_MANAGER}",
            "--ServerApp.allow_remote_access=True",
            "--no-browser"
        ]
