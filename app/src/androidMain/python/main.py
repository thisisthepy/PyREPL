from pycomposeui.runtime import Composable, EmptyComposable, remember_saveable
from pycomposeui.runtime import DefaultCoroutineScope, MainCoroutineScope
from pycomposeui.material3 import SimpleText, SimpleColumn, SimpleRow, SimpleButton
from pycomposeui.ui import modifier

from model.config import ChatHistory
from repl import REPLConfig, LabApp


@Composable
def UiTestCase(text: str = "UiTestCase"):
    SimpleText(text)


@Composable
class UiTest:
    def compose(self, content: Composable = EmptyComposable):
        SimpleColumn(modifier, content=lambda: {
            UiTestCase(text="UiTestCase in UiTest"),
            content()
        })


@Composable
class BasicText:
    @classmethod
    def compose(cls, text: str = "BasicText"):
        SimpleText(text)


@Composable
class RichText(Composable):
    @staticmethod
    def compose(content: Composable = EmptyComposable):
        SimpleColumn(modifier, content=Composable(lambda: {
            BasicText("Basic Text inside of Rich Text"),
            SimpleRow(lambda: {
                BasicText("Row Left Side  "),
                BasicText("Row Right Side")
            }),
            content()
        }))


@Composable
def App():
    messages = remember_saveable("")
    status = remember_saveable("")
    count = remember_saveable(0)

    scope = DefaultCoroutineScope()
    main_scope = MainCoroutineScope()

    user_prompt = remember_saveable("안녕하세요!")

    def change_prompt(prompt: str):
        user_prompt.setValue(prompt)

    llama3 = lambda chat_history, user_prompt, *args: []
    token_streamer = lambda tokens, *args: []
    chat_history = ChatHistory()

    def init_llama3():
        def runner():
            nonlocal llama3, token_streamer
            print_state("Getting started...")
            from model import llama3 as _llama3
            token_streamer = _llama3.token_streamer
            llama3 = _llama3.chat
            print_state("Llama3 initialized")

        scope.launch(runner)

    def print_state(text: str):
        status.setValue(status.getValue() + "  " + text)

    def print_messages(text: str):
        messages.setValue(messages.getValue() + text)

    def run_llama3(printer: callable = lambda x: print(x, end="", flush=True)):
        _user_prompt = user_prompt.getValue()

        if llama3 is None:
            print_state("Llama3 not initialized!!")
        else:
            print_state("Inference...")

            def runner():
                for chunk in token_streamer(*llama3(chat_history, _user_prompt)):
                    printer(chunk)
                printer("\n")
                print_state("Done!")

            scope.launch(runner)

    def run_jupyter():
        scope.launch(lambda: LabApp.launch_instance(REPLConfig.LAB_CONFIG))

    SimpleColumn(modifier, content=lambda: {
        SimpleText(f"Current User Prompt:  {user_prompt.getValue()}"),
        SimpleText(f"Log:{status.getValue()}"),
        SimpleText(""),
        SimpleText(messages.getValue()),
        SimpleButton(
            onclick=init_llama3,
            content=lambda: {
                SimpleText("Init Llama3")
            }
        ),
        SimpleButton(
            onclick=lambda: run_llama3(printer=print_messages),
            content=lambda: {
                SimpleText(f"Send User Prompt")
            }
        ),
        SimpleButton(
            onclick=lambda: {
                change_prompt("오늘 날씨는 어때요?")
            },
            content=lambda: {
                SimpleText(f"Change Prompt")
            }
        ),
        SimpleButton(
            onclick=run_jupyter,
            content=lambda: {
                SimpleText(f"Run Jupyter")
            }
        )
    })
