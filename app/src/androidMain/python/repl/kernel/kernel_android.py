from __future__ import annotations

from typing import Optional, Any, Dict, List
import signal
import time
import sys
import os

from jupyter_server.services.kernels.kernelmanager import ServerKernelManager
import jupyter_client.provisioning as provisioning
from jupyter_client import KernelConnectionInfo

from ipykernel.kernelapp import IPKernelApp
from IPython import get_ipython

from java import jclass
from java.lang import Integer
from android.content import Intent
from com.chaquo.python import Python

from repl import InAppKernelServiceBase
from repl import UIThreadKernelService

app = Python.getPlatform().getApplication()


def prepare_kernel():
    """ Will be called from the InAppKernelService (Multi-Process) """
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    stdin_file = os.path.join(os.environ['HOME'], ".jupyter", "lab", "stdin.redirected")
    stdout_file = os.path.join(os.environ['HOME'], ".jupyter", "lab", "stdout.redirected")
    stderr_file = os.path.join(os.environ['HOME'], ".jupyter", "lab", "stderr.redirected")

    if not os.path.isdir(os.path.dirname(stdin_file)):
        os.makedirs(os.path.dirname(stdin_file))

    sys.stdin, sys.stdout, sys.stderr = [open(file, "w+") for file in [stdin_file, stdout_file, stderr_file]]


def start_kernel(workdir: str | None, filename: str):
    """ Will be called from the InAppKernelService (Multi-Process) """
    if workdir is not None:
        os.chdir(workdir)
    IPKernelApp.launch_instance(["-f", filename])


def interrupt_kernel(signum: int = signal.SIGINT):
    """ Send an interrupt signal to the kernel """
    ipython = get_ipython()
    if ipython is not None and signum == signal.SIGINT:
        print("Interrupting cell...")
        ipython.kernel.interrupt()  # TODO: Not working properly
    else:
        print("Interrupting kernel...")
        os.kill(os.getpid(), signum)


class InAppKernelManager(ServerKernelManager):
    async def start_kernel(self, *args, **kwargs):
        return await super().start_kernel(*args, **kwargs)

    async def restart_kernel(self, *args, **kwargs):
        return await super().restart_kernel(*args, **kwargs)

    async def shutdown_kernel(self, *args, **kwargs):
        return await super().shutdown_kernel(*args, **kwargs)

    async def interrupt_kernel(self, *args, **kwargs):
        return await super().interrupt_kernel(*args, **kwargs)


class UIThreadKernelManager(ServerKernelManager):
    """ KernelManager that will run the kernel in the UI thread """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kernel_service_class = UIThreadKernelService.getClass()

    def _send_intent(self, stop=False, **extras):
        intent = Intent(app, self.kernel_service_class)
        for key, value in extras.items():
            intent.putExtra(key, value)

        if stop:
            app.stopService(intent)
        else:
            app.startService(intent)

    def is_alive(self):
        activity_manager = app.getSystemService(app.ACTIVITY_SERVICE)
        for service_info in activity_manager.getRunningServices(Integer.MAX_VALUE).toArray():
            if service_info.service.getClassName() == self.kernel_service_class.getName():
                return True
        return False

    async def start_kernel(self, *args, **kwargs):
        return await super().start_kernel(*args, **kwargs)

    async def _async_launch_kernel(self, kernel_cmd: List[str], **kwargs: Any) -> None:
        if self.is_alive():
            raise RuntimeError("Only one kernel can be run at a time with the UI thread mode.")
        self._send_intent(workdir=kwargs['cwd'], filename=kernel_cmd[-1])

    async def restart_kernel(self, *args, **kwargs):
        return await super().restart_kernel(*args, **kwargs)

    async def shutdown_kernel(self, *args, **kwargs):
        return await super().shutdown_kernel(*args, **kwargs)

    async def _async_kill_kernel(self, restart: bool = False) -> None:
        self._send_intent(stop=True)
        start_time = time.time()
        while self.is_alive():
            if time.time() > start_time + 5:
                raise RuntimeError("Failed to kill kernel.")
            time.sleep(0.1)

    async def interrupt_kernel(self, *args, **kwargs):
        return  # await super().interrupt_kernel(*args, **kwargs)


class InAppLocalPrivateProvisioner(provisioning.local_provisioner.LocalProvisioner):
    """ Android LocalProvisioner that will start the kernel in a separate process """

    class Process:
        """ Represents a kernel process """
        max_workers = InAppKernelServiceBase.MAX_WORKERS  # Maximum number of kernels that can be started simultaneously
                                                        #  (declared in AndroidManifest.xml)
        kernel_service_basename = InAppKernelServiceBase.getClass().getName().replace("Base", "")
        _reserved_procs = []
        intent_wait_time = 5

        @classmethod
        def reserve_new_proc_name(cls):
            new_id = next((proc for proc in list(range(cls.max_workers)) if proc not in cls._reserved_procs), None)
            if new_id is None:
                raise RuntimeError(f"Maximum number of kernels({cls.max_workers}) reached."
                                + f" Please exit the kernel that is not in use and try again.")
            cls._reserved_procs.append(new_id)
            return new_id

        def release_proc_name(self):
            self._reserved_procs.remove(self.process_name)

        def __init__(self, cmd: List[str], **kwargs):
            self.process_name = self.reserve_new_proc_name()
            self.kernel_service_class = jclass(self.kernel_service_basename + str(self.process_name)).getClass()
            self._send_intent(workdir=kwargs['cwd'], filename=cmd[-1])

            start_time = time.time()
            while self.process_info is None:
                if time.time() > start_time + self.intent_wait_time:
                    raise RuntimeError("Failed to start kernel process.")
                time.sleep(0.1)

            class DummyIOStream:
                def close(self):
                    pass

            self.pid = self.process_info.pid
            self.stdin = DummyIOStream()
            self.stdout = DummyIOStream()
            self.stderr = DummyIOStream()

        def __del__(self):
            self.release_proc_name()

        def _send_intent(self, stop=False, **extras):
            """ Send an intent to the InAppKernelService """
            intent = Intent(app, self.kernel_service_class)
            for key, value in extras.items():
                intent.putExtra(key, value)

            if stop:
                app.stopService(intent)
            else:
                app.startService(intent)

        @property
        def process_info(self):
            """ Get the process info
            :return: The process info if the kernel is running, None otherwise
            """
            activity_manager = app.getSystemService(app.ACTIVITY_SERVICE)
            for p_info in activity_manager.getRunningAppProcesses(Integer.MAX_VALUE).toArray():
                if ":".join(["", *p_info.processName.split(":")[1:]]) == f":kernel{self.process_name}":
                    return p_info
            return None

        def poll(self) -> None | int:
            """ Check if the kernel is dead
            :return: None if the kernel is running, 0 if the kernel is dead
            """
            if self.process_info is None:
                return 0
            return None

        def wait(self):
            while self.poll() is None:
                time.sleep(0.1)
            return 0

        def send_signal(self, signum: int):
            self._send_intent(signum=signum)
            time.sleep(1)

        def kill(self):
            self._send_intent(kill=True)

        def terminate(self):
            self._send_intent(kill=True)

    async def poll(self) -> Optional[int]:
        return await super().poll()

    async def wait(self) -> Optional[int]:
        return await super().wait()

    async def send_signal(self, signum: int) -> None:
        self.process.send_signal(signum)

    async def kill(self, restart: bool = False) -> None:
        if self.process:
            try:
                self.process.kill()
            except OSError as e:
                self._tolerate_no_process(e)

    async def terminate(self, restart: bool = False) -> None:
        if self.process:
            try:
                self.process.terminate()
            except OSError as e:
                self._tolerate_no_process(e)

    async def pre_launch(self, **kwargs: Any) -> Dict[str, Any]:
        return await super().pre_launch(**kwargs)

    async def launch_kernel(self, cmd: List[str], **kwargs: Any) -> KernelConnectionInfo:
        scrubbed_kwargs = self._scrub_kwargs(kwargs)
        self.process = self.Process(cmd, **scrubbed_kwargs)
        pgid = None
        if hasattr(os, "getpgid"):
            try:
                pgid = os.getpgid(self.process.pid)
            except OSError:
                pass

        self.pid = self.process.pid
        self.pgid = pgid
        return self.connection_info


#provisioning.LocalProvisioner = InAppLocalPrivateProvisioner
