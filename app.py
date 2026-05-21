import os
from flask import Flask, request, abort
import google.generativeai as genai

from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError

from linebot.v3.webhooks import MessageEvent
from linebot.v3.webhooks.models import TextMessageContent

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

app = Flask(__name__)

# =========================
# LINE設定
# =========================

configuration = Configuration(
    access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
)

handler = WebhookHandler(
    os.environ.get("LINE_CHANNEL_SECRET")
)

# =========================
# Gemini設定
# =========================

genai.configure(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Geminiモデル
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# 動作確認
# =========================

@app.route("/")
def home():
    return "LINE Gemini Bot is running!"

# =========================
# LINE Webhook
# =========================

@app.route("/callback", methods=["POST"])
def callback():

    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        print("Invalid signature")

        abort(400)

    return "OK"

# =========================
# メッセージ受信
# =========================

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_message = event.message.text

    try:
        # Geminiへ送信
        response = model.generate_content(user_message)

        reply_text = response.text

    except Exception as e:
        print(e)

        reply_text = "エラーが発生しました"

    # LINE返信
    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=reply_text
                    )
                ]
            )
        )

# =========================
# 起動
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
