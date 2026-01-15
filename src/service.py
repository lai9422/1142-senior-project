from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import LineBotApiError
from src.line_bot_api import line_bot_api, handler

# 註冊處理文字訊息的事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(f"準備回傳訊息: {msg}")

    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )
        print("✅ 回傳成功！")
    except LineBotApiError as e:
        print(f"❌ 回傳失敗 (Token可能錯了): {e.status_code} {e.message}")