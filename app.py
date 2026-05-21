From flask import Flask, request

import os

import google.generativeai as genai

from linebot.v3 import WebhookHandler

from linebot.v3.messaging import (

    Configuration,

    ApiClient,

    MessagingApi,

    ReplyMessageRequest,

    TextMessage

)

from linebot.v3.webhooks import (

    MessageEvent,

    TextMessageContent

)

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

configuration = Configuration(

    access_token=LINE_CHANNEL_ACCESS_TOKEN

)

handler = WebhookHandler(LINE_CHANNEL_SECRET)

model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/callback", methods=["POST"])

def callback():

    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)

    handler.handle(body, signature)

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)

def handle_message(event):

    user_message = event.message.text

    response = model.generate_content(user_message)

    ai_reply = response.text

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(

            ReplyMessageRequest(

                reply_token=event.reply_token,

                messages=[TextMessage(text=ai_reply)]

            )

        )

if __name__ == "__main__":

    app.run(port=5000)
