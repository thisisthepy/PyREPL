from pythonx.compose.runtime import Composable, EmptyComposable, remember_saveable
from pythonx.compose.runtime import DefaultCoroutineScope, MainCoroutineScope
from pythonx.compose.material3 import Text, Column, Row, Button
from pythonx.compose.ui import modifier

from android.content import Intent
from android.net import Uri
from pythonx.compose.ui.platform import LocalContext

import time
from model.config import ChatHistory
from repl import REPLConfig, send_server_launch_intent, kernel


config = REPLConfig(manager_class=kernel.UIThreadKernelManager)


@Composable
def UiTestCase(text: str = "UiTestCase"):
    Text(text)


@Composable
class UiTest:
    def compose(self, content: Composable = EmptyComposable):
        Column(modifier, content=lambda: {
            UiTestCase(text="UiTestCase in UiTest"),
            content()
        })


@Composable
class BasicText:
    @classmethod
    def compose(cls, text: str = "BasicText"):
        Text(text)


@Composable
class RichText(Composable):
    @staticmethod
    def compose(content: Composable = EmptyComposable):
        Column(modifier, content=Composable(lambda: {
            BasicText("Basic Text inside of Rich Text"),
            Row(lambda: {
                BasicText("Row Left Side  "),
                BasicText("Row Right Side")
            }),
            content()
        }))


@Composable
class App(Composable):
    versions = dict()

    @classmethod
    def update(cls, new_view):
        if cls.count.getValue() == 0:
            cls.versions[1] = new_view
            cls.count.setValue(1)
        elif cls.count.getValue() == 1:
            cls.versions[2] = new_view
            cls.count.setValue(2)
            cls.versions[1] = lambda: None
        else:
            cls.versions[1] = new_view
            cls.count.setValue(1)
            cls.versions[2] = lambda: None

    @classmethod
    def compose(cls):
        context = LocalContext.current

        cls.messages = messages = remember_saveable("")
        cls.status = status = remember_saveable("")
        cls.count = remember_saveable(0)

        cls.scope = DefaultCoroutineScope()
        cls.main_scope = MainCoroutineScope()

        cls.user_prompt = user_prompt = remember_saveable("안녕하세요!")

        def run_jupyter():
            browser_intent = Intent(Intent.ACTION_VIEW, Uri.parse(config.uri))

            def runner():
                send_server_launch_intent(context, config)
                time.sleep(1)
                context.startActivity(browser_intent)

            cls.scope.launch(runner)

        @Composable
        def View():
            Text("PyComposeUI PyREPL 데모에 오신 것을 환영합니다!")
            Text("- Android Demo v.0.0.1")
            Text("")
            Text("")
            Text("[Jupyter Lab 연결 정보]")
            Text(f">  IP: {config.ip}")
            Text(f">  PORT: {config.port}")
            Text(f">  PASSWORD: {config.password}")
            Text("")

            Button(
                onclick=lambda: None,
                content=lambda: {
                    Text(f"실행 모드 변경 (현재 옵션: UI 스레드 동기화 모드)")
                }
            )

            Button(
                onclick=lambda: None,
                content=lambda: {
                    Text(f"브라우저: 기본 브라우저 열기")
                }
            )

            Button(
                onclick=run_jupyter,
                content=lambda: {
                    Text(f"Jupyter Lab 실행")
                }
            )

        cls.versions[0] = View

        Column(modifier, content=lambda: {
            cls.versions[cls.count.getValue()]()
        })


def init_llama3():
    def runner():
        global llama3, token_streamer
        print_state("Getting started...")
        from model import llama3 as _llama3
        token_streamer = _llama3.token_streamer
        llama3 = _llama3.chat
        print_state("Llama3 initialized")

    App.scope.launch(runner)


llama3 = lambda chat_history, user_prompt, *args: []
token_streamer = lambda tokens, *args: []
chat_history = ChatHistory()


def change_prompt(prompt: str):
    App.user_prompt.setValue(prompt)


def print_state(text: str):
    App.status.setValue(App.status.getValue() + "  " + text)


def print_messages(text: str):
    App.messages.setValue(App.messages.getValue() + text)


def run_llama3(printer: callable = lambda x: print(x, end="", flush=True)):
    _user_prompt = App.user_prompt.getValue()

    if llama3 is None:
        print_state("Llama3 not initialized!!")
    else:
        print_state("Inference...")

        def runner():
            for chunk in token_streamer(*llama3(chat_history, _user_prompt)):
                printer(chunk)
            printer("\n")
            print_state("Done!")

        App.scope.launch(runner)


@Composable
def LlamaView():
    Text(f"Current User Prompt:  {App.user_prompt.getValue()}")
    Text(f"Log:{App.status.getValue()}")
    Text("")
    Text(App.messages.getValue())
    Button(
        onclick=init_llama3,
        content=lambda: {
            Text("Init Llama3")
        }
    )
    Button(
        onclick=lambda: run_llama3(printer=print_messages),
        content=lambda: {
            Text(f"Send User Prompt")
        }
    )
    Button(
        onclick=lambda: {
            change_prompt("오늘 날씨는 어때요?")
        },
        content=lambda: {
            Text(f"Change Prompt")
        }
    )
