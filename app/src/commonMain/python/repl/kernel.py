import time

from ipykernel import kernelapp
from jupyter_server.services.kernels.kernelmanager import ServerKernelManager


class InAppKernelManager(ServerKernelManager):
    def start_kernel(self, *args, **kwargs):
        #if self.is_alive():
        #    raise RuntimeError("Can only run one kernel at a time")

        kernelapp.launch_new_instance(*args, **kwargs)

        # Return a non-None value so self.has_kernel will be true. This will be assigned to
        # self.kernel, but we override all the methods which access that.
        return True

    def shutdown_kernel(self):
        time.sleep(0.1)  # Give the kernel a chance to shut down gracefully.
        if self.is_alive():
            raise RuntimeError("Failed to kill kernel")

    # Interruption would normally be done by sending SIGINT to the kernel process, but signals
    # can only be handled by the main thread, which is reserved for the Android event loop.
    def interrupt_kernel(self):
        raise RuntimeError("Kernel interrupt is not implemented. Use 'Restart' instead.")
