from jupyter_server.services.kernels.kernelmanager import ServerKernelManager
from ipykernel.kernelapp import IPKernelApp
import typing as t
import datetime
import sys
import os
import re

from java import dynamic_proxy
from android.content import Intent
from com.chaquo.python import Python
from repl import InAppKernelService

app = Python.getPlatform().getApplication()


def send_intent(**extras):
    intent = Intent(app, InAppKernelService.getClass())
    for key, value in extras.items():
        intent.putExtra(key, value)
    app.startService(intent)


def start_kernel(workdir: str, filename: str):
    os.chdir(workdir)
    sys.argv[1:] = ["-f", filename]
    IPKernelApp.launch_instance()


class InAppKernelManager(ServerKernelManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_activity = datetime.datetime.now()

    async def start_kernel(self, *args, **kwargs):
        return await super().start_kernel(*args, **kwargs)

    async def _async_launch_kernel(self, kernel_cmd: t.List[str], **kwargs: t.Any) -> None:
        print("Starting kernel with arguments", kernel_cmd)
        send_intent(workdir=kwargs['cwd'], filename=kernel_cmd[-1])

    async def restart_kernel(self, *args, **kwargs):
        return await super().restart_kernel(*args, **kwargs)

    async def shutdown_kernel(self, *args, **kwargs):
        return await super().shutdown_kernel(*args, **kwargs)

    async def interrupt_kernel(self, *args, **kwargs):
        return await super().interrupt_kernel(*args, **kwargs)
