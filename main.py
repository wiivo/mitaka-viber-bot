from flask import Flask, request, Response
import logging

from multiprocessing import Process
import json
import urllib.request

from viberbot import Api
from botConfiguration import botConfig

from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.picture_message import PictureMessage

from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberConversationStartedRequest

from functionality.interpreter import Interpreter

# setWebhook sends a post request to the viber webhook url
# curl -# -i -g -H "X-Viber-Auth-Token:token" -d @viber.json -X POST https://chatapi.viber.com/pa/set_webhook -v
def setWebhook():
    f = open('viber.json')
    data = json.load(f)
    data = json.dumps(data).encode("utf-8")

    headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    }

    url = "https://chatapi.viber.com/pa/set_webhook"

    try:
        req = urllib.request.Request(url, data, headers)
        urllib.request.urlopen(req)
    except Exception as e:
        print(e)

# setup code
app = Flask(__name__)
viber = Api(botConfig)

interp = Interpreter()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@app.route("/", methods=["POST"])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    if not viber.verify_signature(
        request.get_data(), request.headers.get("X-Viber-Content-Signature")
    ):
        return Response(status=403)
    
    # gets message
    viber_request = viber.parse_request(request.get_data())

    # if else sequence depending on what type of message it is
    if isinstance(viber_request, ViberMessageRequest):
        message = interp.executeCommand(viber_request.message.text.upper())

        # if command is valid, it sends it, else the bot replies with "Sorry, I can't do that"
        if message != None:
            # if message is a tuple it is a picture message, else it's just a string
            if isinstance(message, tuple):
                viber.send_messages(
                    viber_request.sender.id,
                    [PictureMessage(media=message[0], text=message[1])],
                )
            else:
                viber.send_messages(
                    viber_request.sender.id, [TextMessage(text=message)]
                )
        else:
            viber.send_messages(
                viber_request.sender.id,
                [TextMessage(text="Извинявай, не знам какво искаш от мен.")],
            )
    # if you just started a convo with the bot, it replies with "hello, what can i do for you"
    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(
            viber_request.user.id,
            [
                TextMessage(
                    text="Здрасти, аз съм Митака, какво мога да направя за теб?"
                ),
            ],
        )
    # if something goes wrong 
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn(
            "client failed receiving message. failure: {0}".format(viber_request)
        )

    return Response(status=200)

if __name__ == "__main__":
    # function to set webhook, runs in seperate process
    p = Process(target=setWebhook)
    p.start() 
    app.run(port=8087, debug=True, use_reloader=False)
    p.join()
