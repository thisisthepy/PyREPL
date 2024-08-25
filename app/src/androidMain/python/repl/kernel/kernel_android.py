from typing import Any

from jupyter_client import KernelProvisionerBase
from jupyter_server.services.kernels.kernelmanager import ServerKernelManager
from jupyter_client.provisioning.factory import KernelProvisionerFactory
from ipykernel.kernelapp import IPKernelApp
import typing as t
import datetime
import sys
import os

from java import jclass
from java.lang import Integer
from android.content import Intent
from com.chaquo.python import Python

from repl import InAppKernelServiceBase

app = Python.getPlatform().getApplication()


def start_kernel(workdir: str, filename: str):
    """ Will be called from the InAppKernelService (Multi-Process) """
    os.chdir(workdir)
    sys.argv[1:] = ["-f", filename]

    stdin_file = os.path.join(os.environ['HOME'], ".tmp", "lab", "stdin.redirected")
    stdout_file = os.path.join(os.environ['HOME'], ".tmp", "lab", "stdout.redirected")
    stderr_file = os.path.join(os.environ['HOME'], ".tmp", "lab", "stderr.redirected")

    if not os.path.isdir(os.path.dirname(stdin_file)):
        os.makedirs(os.path.dirname(stdin_file))

    sys.stdin, sys.stdout, sys.stderr = [open(file, "w+") for file in [stdin_file, stdout_file, stderr_file]]
    IPKernelApp.launch_instance()


def send_intent(service, **extras):
    """ Send an intent to the InAppKernelService """
    intent = Intent(app, service)
    for key, value in extras.items():
        intent.putExtra(key, value)
    app.startService(intent)


class InAppKernelManager(ServerKernelManager):
    """ Custom KernelManager that will start the kernel in a separate process """

    max_workers = InAppKernelServiceBase.maxWorkers  # Maximum number of kernels that can be started simultaneously
                                                    # (declared in AndroidManifest.xml)
    kernel_service_basename = InAppKernelServiceBase.getClass().getName().replace("Base", "")
    _reserved_pids = []

    def reserve_new_pid(self):
        new_id = next((process for process in list(range(self.max_workers)) if process not in self._reserved_pids), None)
        if new_id is None:
            raise RuntimeError(f"Maximum number of kernels({self.max_workers}) reached."
                            + f" Please exit the kernel that is not in use and try again.")
        self._reserved_pids.append(new_id)
        return new_id

    def release_pid(self, process_id):
        self._reserved_pids.remove(process_id)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_activity = datetime.datetime.now()
        self.process_id = self.reserve_new_pid()
        self.kernel_service_class = jclass(self.kernel_service_basename + str(self.process_id)).getClass()

    def __del__(self):
        self.release_pid(self.process_id)

    @property
    def is_running(self) -> bool:
        activity_manager = app.getSystemService(app.ACTIVITY_SERVICE)
        for service_info in activity_manager.getRunningServices(Integer.MAX_VALUE).toArray():
            if service_info.service.getClassName() == self.kernel_service_class.getName():
                return True
        return False

    async def start_kernel(self, *args, **kwargs):
        return await super().start_kernel(*args, **kwargs)

    async def _async_launch_kernel(self, kernel_cmd: t.List[str], cwd="", **kwargs: t.Any) -> None:
        if self.is_running:
            raise RuntimeError("Kernel already running.")
        send_intent(service=self.kernel_service_class, workdir=cwd, filename=kernel_cmd[-1])

    async def restart_kernel(self, *args, **kwargs):
        return await super().restart_kernel(*args, **kwargs)

    async def shutdown_kernel(self, *args, **kwargs):
        return await super().shutdown_kernel(*args, **kwargs)

    async def _async_kill_kernel(self, restart: bool = False) -> None:
        app.stopService(send_intent(service=self.kernel_service_class))
        import time
        start_time = time.time()
        while self.is_running:
            if time.time() > start_time + 0.5:
                raise RuntimeError("Failed to kill kernel.")
            time.sleep(0.1)

    async def interrupt_kernel(self, *args, **kwargs):
        #return await super().interrupt_kernel(*args, **kwargs)
        pass


class InAppKernelProvisionerFactory(KernelProvisionerFactory):
    """ Android KernelProvisionerFactory that will use the InAppKernelManager """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def is_provisioner_available(self, kernel_spec: Any) -> bool:
        return super().is_provisioner_available(kernel_spec)

    def create_provisioner_instance(self, kernel_id: str, kernel_spec: Any, parent: Any) -> KernelProvisionerBase:
        return super().create_provisioner_instance(kernel_id, kernel_spec, parent)
