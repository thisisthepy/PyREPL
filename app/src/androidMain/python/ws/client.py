import websocket
from model.config import ChatHistory
import json

chat_history = ChatHistory()

WEBSOCKET_URL = "ws://127.0.0.1:8000/ws"


def on_open(ws):
    print("Websocket connection is now open")

    data = get_user_message().strip()
    if data:
        ws.send(json.dumps(chat_history))  # chat history 전송
        ws.send(data)  # user prompt 전송
        chat_history.append("user", data)  # chat history 업데이트
        update_screen(data, True)  # 화면 업데이트
        set_user_message("")  # 입력창 초기화


def on_message(ws, message):
    print("Message received:", message)
    if message == "<EOS>":
        ws.close()
        return

    if message:
        update_screen(message, False)


def on_close(ws, *_):
    print("Connection closed")


def get_user_message():
    """ should be overridden by the platform-specific implementation """
    return ""


def set_user_message(message: str):
    """ should be overridden by the platform-specific implementation """
    pass


def update_screen(text: str, user_content: bool = True):
    """ should be overridden by the platform-specific implementation """
    pass


def run_websocket():
    ws = websocket.WebSocketApp(WEBSOCKET_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_close=on_close,
                                on_error=lambda w, e: print("Websocket error", e))

    ws.run_forever()
