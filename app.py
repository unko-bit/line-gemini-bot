import os
from flask import Flask, request, abort

import google.generativeai as genai

from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage as LineTextMessage
)
from linebot.v3.webhooks import TextMessageContent
from linebot.exceptions import InvalidSignatureException

app = Flask(__name__)

# LINE設定
configuration = Configuration(
    access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
)

handler = WebhookHandler(
    os.environ.get("LINE_CHANNEL_SECRET")
)

# Gemini設定
genai.configure(
    api_key=os.environ.get("GEMINI_API_KEY")
)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureException:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_message = event.message.text

    # Gemini呼び出し
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(user_message)

    reply_text = response.text

    # LINE返信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    LineTextMessage(text=reply_text)
                ]
            )
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
