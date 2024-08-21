import os
import sys
import json
import runpy

from jupyter_client import ioloop

from android.content import Intent


def main(intent):
    os.chdir(intent.getStringExtra("jupyter_cwd"))
    connection_filename = intent.getStringExtra("jupyter_connection_file")
    print("Connection file: " +  # Use compact representation for log.
          json.dumps(json.load(open(connection_filename))).strip())

    # The kernel redirects standard streams to the notebook, and does not clean up after
    # itself.
    stdin, stdout, stderr = sys.stdin, sys.stdout, sys.stderr
    try:
        sys.argv[1:] = ["-f", connection_filename]
        runpy.run_module("ipykernel_launcher", run_name="__main__")
    except SystemExit as e:
        if e.code == 0:
            pass
    finally:
        sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr


class ChaquopyManager(ioloop.IOLoopKernelManager):
    def _launch_kernel(self, kernel_cmd, **kwargs):
        if self.is_alive():
            raise RuntimeError("Can only run one kernel at a time")

        kwargs.pop("env", None)  # Unnecessary, and could cause complications.
        cwd = kwargs.pop("cwd")
        if kwargs:
            raise ValueError(f"Unknown kwargs: {kwargs}")

        # See ipykernel.kernelspec.make_ipkernel_cmd.
        match = re.search(fr"^{sys.executable} -m ipykernel_launcher -f (\S+)$",
                          " ".join(kernel_cmd))
        if not match:
            raise ValueError(f"Unknown command: {kernel_cmd}")
        app.startService(self._new_intent(jupyter_cwd=cwd,
                                          jupyter_connection_file=match.group(1)))

        # Return a non-None value so self.has_kernel will be true. This will be assigned to
        # self.kernel, but we override all the methods which access that.
        return True

    def _kill_kernel(self):
        app.stopService(self._new_intent())
        start_time = time.time()
        while self.is_alive():
            if time.time() > start_time + SHUTDOWN_TIMEOUT:
                raise RuntimeError("Failed to kill kernel")
            time.sleep(0.1)

    # Interruption would normally be done by sending SIGINT to the kernel process, but signals
    # can only be handled by the main thread, which is reserved for the Android event loop.
    def interrupt_kernel(self):
        raise RuntimeError("Kernel interrupt is not implemented. Use 'Restart' instead.")

    def signal_kernel(self, signum):
        pass

    def is_alive(self):
        am = app.getSystemService(app.ACTIVITY_SERVICE)
        for service_info in am.getRunningServices(Integer.MAX_VALUE).toArray():
            if service_info.service.getClassName() == KernelService.getClass().getName():
                return True
        return False

    def _new_intent(self, **extras):
        intent = Intent(app, KernelService.getClass())
        for key, value in extras.items():
            intent.putExtra(key, value)
        return intent
