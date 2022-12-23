import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message
from transitions.extensions import GraphMachine

load_dotenv()


machine = TocMachine(
    states=['input_server',
        'input_place',
        'input_tag',
        'show_recommand',
        'input_sour','input_non_sour_flavor','input_sour_flavor','show_non_sour_rm','show_sour_rm'],
    transitions=[
        {'trigger': 'advance', 'source': 'user', 'dest': 'input_server', 'conditions': 'is_going_to_input_server'},
        {'trigger': 'advance', 'source': 'input_server', 'dest': 'input_place', 'conditions': 'is_going_to_input_place'},
        {'trigger': 'advance', 'source': 'input_place', 'dest': 'input_tag', 'conditions': 'is_going_to_input_tag'},
        {'trigger': 'advance', 'source': 'input_tag', 'dest': 'show_recommand', 'conditions': 'is_going_to_show_recommand'},
        {'trigger': 'advance', 'source': 'show_recommand', 'dest': 'input_server', 'conditions': 'is_going_to_input_server'},
        {'trigger': 'advance', 'source': 'input_server', 'dest': 'input_sour', 'conditions': 'is_going_to_input_sour'},
        {'trigger': 'advance', 'source': 'input_sour', 'dest': 'input_non_sour_flavor', 'conditions': 'is_going_to_input_non_sour_flavor'},
        {'trigger': 'advance', 'source': 'input_sour', 'dest': 'input_sour_flavor', 'conditions': 'is_going_to_input_sour_flavor'},
        {'trigger': 'advance', 'source': 'input_non_sour_flavor', 'dest': 'show_non_sour_rm', 'conditions': 'is_going_to_show_non_sour_rm'},
        {'trigger': 'advance', 'source': 'input_sour_flavor', 'dest': 'show_sour_rm', 'conditions': 'is_going_to_show_sour_rm'},
        {'trigger': 'advance', 'source': 'show_non_sour_rm', 'dest': 'input_server', 'conditions': 'is_going_to_input_server'},
        {'trigger': 'advance', 'source': 'show_sour_rm', 'dest': 'input_server', 'conditions': 'is_going_to_input_server'},
        {"trigger": "go_back", "source": ['input_server',
                'input_place',
                'input_tag',
                'show_recommand','input_sour','input_non_sour_flavor','input_sour_flavor','show_non_sour_rm','show_sour_rm'], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


# @app.route("/show-fsm", methods=["GET"])
# def show_fsm():
#     machine.get_graph().draw("fsm.png", prog="dot", format="png")
#     return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
