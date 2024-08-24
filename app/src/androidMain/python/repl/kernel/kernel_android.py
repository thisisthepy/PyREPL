from jupyter_server.services.kernels.kernelmanager import ServerKernelManager
from ipykernel.kernelapp import IPKernelApp
import typing as t
import datetime
import time
import sys
import os

from java.lang import Integer
from android.content import Intent
from com.chaquo.python import Python
from repl import InAppKernelService

from ipykernel import iostream

app = Python.getPlatform().getApplication()


def send_intent(**extras):
    intent = Intent(app, InAppKernelService.getClass())
    for key, value in extras.items():
        intent.putExtra(key, value)
    app.startService(intent)


def start_kernel(workdir: str, filename: str):
    os.chdir(workdir)
    sys.argv[1:] = ["-f", filename]

    stdin_file = os.path.join(os.environ['HOME'], ".tmp", "lab", "stdin.redirected")
    stdout_file = os.path.join(os.environ['HOME'], ".tmp", "lab", "stdout.redirected")
    stderr_file = os.path.join(os.environ['HOME'], ".tmp", "lab", "stderr.redirected")

    if not os.path.isdir(os.path.dirname(stdin_file)):
        os.makedirs(os.path.dirname(stdin_file))

    sys.stdin, sys.stdout, sys.stderr = [open(file, "w+") for file in [stdin_file, stdout_file, stderr_file]]
    IPKernelApp.launch_instance()


class InAppKernelManager(ServerKernelManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_activity = datetime.datetime.now()

    def is_alive(self):
        am = app.getSystemService(app.ACTIVITY_SERVICE)
        for service_info in am.getRunningServices(Integer.MAX_VALUE).toArray():
            if service_info.service.getClassName() == InAppKernelService.getClass().getName():
                return True
        return False

    async def start_kernel(self, *args, **kwargs):
        return await super().start_kernel(*args, **kwargs)

    async def _async_launch_kernel(self, kernel_cmd: t.List[str], cwd="", **kwargs: t.Any) -> None:
        if self.is_alive():
            raise RuntimeError("Kernel already running")
        print("Starting kernel with arguments", kernel_cmd)
        send_intent(workdir=cwd, filename=kernel_cmd[-1])

    async def restart_kernel(self, *args, **kwargs):
        return await super().restart_kernel(*args, **kwargs)

    async def shutdown_kernel(self, *args, **kwargs):
        return await super().shutdown_kernel(*args, **kwargs)

    async def _async_kill_kernel(self, restart: bool = False) -> None:
        app.stopService(send_intent())
        start_time = time.time()
        while self.is_alive():
            if time.time() > start_time + self.shutdown_wait_time:
                raise RuntimeError("Failed to kill kernel")
            time.sleep(0.1)

    async def interrupt_kernel(self, *args, **kwargs):
        #return await super().interrupt_kernel(*args, **kwargs)
        pass
