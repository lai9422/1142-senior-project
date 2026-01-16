# 引入 Line Bot SDK
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction
)
from linebot.exceptions import LineBotApiError

# 引入專案模組
from src.line_bot_api import line_bot_api, handler
from src.database import get_intents
from src.ai_client import ai_service
from src.text_processor import segment_text
from src.intent_matcher import find_best_match

# ==========================================
# 輔助函式：產生回覆物件
# ==========================================
def get_reply_object(reply_text, action):
    if action == "SHOW_CRISIS_MENU":
        return TextSendMessage(
            text=reply_text,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="撥打 113", text="撥打 113")),
                QuickReplyButton(action=MessageAction(label="撥打 110", text="撥打 110"))
            ])
        )
    elif action == "SHOW_MAIN_MENU":
        return TextSendMessage(
            text=reply_text,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="心情不好", text="心情不好")),
                QuickReplyButton(action=MessageAction(label="關於我", text="關於我"))
            ])
        )
    else:
        return TextSendMessage(text=reply_text)

# ==========================================
# Line Bot 主要處理邏輯
# ==========================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    print(f"📩 收到訊息: {user_msg}")

    # 1. 取得資料 (呼叫 database 模組)
    intents = get_intents()

    # 2. 斷詞 (呼叫 text_processor 模組)
    seg_list = segment_text(user_msg)

    # 3. 判斷意圖 (呼叫 intent_matcher 模組)
    matched_intent = find_best_match(seg_list, intents)

    # 4. 決策與 AI 潤飾 (呼叫 ai_client 模組)
    final_response_text = ""
    action_code = "NONE"

    if matched_intent:
        # 命中意圖 -> 請 AI 潤飾資料庫的回應
        final_response_text = ai_service.polish_response(
            user_msg, matched_intent['response'], matched_intent['category']
        )
        action_code = matched_intent['action']
    else:
        # 未命中 -> 預設閒聊模式
        print("🤷‍♂️ 未命中，使用預設回應")
        default_text = "我不太確定你的意思，但我在這裡陪你。你可以多說一點嗎？"
        final_response_text = ai_service.polish_response(user_msg, default_text, "閒聊")
        action_code = "SHOW_MAIN_MENU"

    # 5. 發送回覆
    try:
        reply_obj = get_reply_object(final_response_text, action_code)
        line_bot_api.reply_message(event.reply_token, reply_obj)
        print("✅ 訊息已發送")
    except LineBotApiError as e:
        print(f"❌ Line API 錯誤: {e.status_code} {e.message}")