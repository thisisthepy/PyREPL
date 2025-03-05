from jupyterlab.labapp import LabApp
from .config import REPLConfig

from android.content import Intent
from repl import InAppLabServerService


def run_lab_server(
        ip: str | None = None, port: int | None = None, password: str | None = None, manager: str | None = None,
        config: REPLConfig | None = None
):
    if config is None:
        kwargs = { k: v for k, v in dict(ip=ip, port=port, password=password).items() if v is not None }
        config = REPLConfig(**kwargs)
        if manager is not None:
            config.manager = manager
    LabApp.launch_instance(config.list)


def send_server_launch_intent(context, config: REPLConfig):
    intent = Intent(context, InAppLabServerService.getClass())
    for key, value in config.dict.items():
        intent.putExtra(key, value)
    context.startService(intent)

def send_server_stop_intent(context):
    intent = Intent(context, InAppLabServerService.getClass())
    context.stopService(intent)
