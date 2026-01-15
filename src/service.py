import jieba
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction
)
from linebot.exceptions import LineBotApiError
from src.line_bot_api import line_bot_api, handler

# ==========================================
# 1. 模擬資料庫 (Intents Data)
# ==========================================
# 這裡將你提供的表格轉換為 Python 資料結構
# danger: 5(最高危), 0(一般)
INTENTS = [
    {
        "category": "緊急求助",
        "keywords": ["死", "自殺", "割腕", "藥", "消失", "頂樓"],
        "danger": 5,
        "response": "同學，我感覺到你現在非常痛苦，謝謝你告訴我。這一刻請先停下來，我們很重視你的安全。👇 請點擊下方按鈕，有人會馬上聽你說。",
        "action": "SHOW_CRISIS_MENU"
    },
    {
        "category": "身體界線",
        "keywords": ["摸", "不舒服", "奇怪", "碰", "強迫", "性騷擾"],
        "danger": 3,
        "response": "遇到這樣的情況確實會讓人感到困惑和不舒服。你的感覺很重要。如果是對方未經同意的碰觸，這可能涉及到性騷擾。你想多了解如何保護自己嗎？",
        "action": "LINK_LEGAL_INFO"
    },
    {
        "category": "情緒宣洩",
        "keywords": ["髒", "噁心", "爛", "洗澡", "洗不乾淨"],
        "danger": 2,
        "response": "親愛的，那不是你的錯，也不是你髒。這種「洗不乾淨」的感覺是創傷後常見的生理反應，是身體想保護你的機制...",
        "action": "NONE"
    },
    {
        "category": "測試/打招呼",
        "keywords": ["在嗎", "哈囉", "嗨", "誰", "聊聊", "你好"],
        "danger": 0,
        "response": "嗨！我在這裡。我是專門陪你的小幫手。這裡很安全，你可以說說任何你想說的事，或是點選單看看我能幫什麼忙。",
        "action": "SHOW_MAIN_MENU"
    }
]

# ==========================================
# 2. 輔助函式：處理特殊動作 (Action)
# ==========================================
def get_reply_object(reply_text, action):
    """
    根據 Action 類型，決定要回傳單純文字，還是帶有按鈕(QuickReply)的訊息
    """
    if action == "SHOW_CRISIS_MENU":
        # 範例：加上緊急求助按鈕
        return TextSendMessage(
            text=reply_text,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="打給 113", text="撥打 113")),
                QuickReplyButton(action=MessageAction(label="打給 110", text="撥打 110"))
            ])
        )
    elif action == "SHOW_MAIN_MENU":
        # 範例：加上主選單按鈕
        return TextSendMessage(
            text=reply_text,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="心情不好", text="心情不好")),
                QuickReplyButton(action=MessageAction(label="關於我", text="關於我"))
            ])
        )
    else:
        # 預設只回傳文字
        return TextSendMessage(text=reply_text)

# ==========================================
# 3. 主要訊息處理邏輯
# ==========================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    print(f"收到訊息: {user_msg}")

    # --- 步驟 A: Jieba 斷詞 ---
    # cut_all=False 精確模式 (適合文本分析)
    seg_list = list(jieba.cut(user_msg, cut_all=False))
    print(f"斷詞結果: {seg_list}")

    # --- 步驟 B: 關鍵字比對 ---
    matched_intent = None
    
    # 遍歷所有意圖，尋找是否有關鍵字出現在斷詞結果中
    found_intents = []
    for intent in INTENTS:
        # 檢查該意圖的所有關鍵字，是否有任何一個出現在使用者的斷詞清單中
        # 使用 set intersection (交集) 來快速比對
        if set(intent["keywords"]) & set(seg_list):
            found_intents.append(intent)
    
    # --- 步驟 C: 決定最佳回應 (邏輯：取危險指數最高的) ---
    if found_intents:
        # 根據 danger 欄位由大到小排序，取第一個
        found_intents.sort(key=lambda x: x["danger"], reverse=True)
        matched_intent = found_intents[0]
        print(f">> 命中意圖: {matched_intent['category']} (危險級別: {matched_intent['danger']})")
    else:
        # 如果都沒命中，可以設定一個預設回應 (Fallback)
        print(">> 未命中任何關鍵字，使用預設回應")
        matched_intent = {
            "response": "我不太確定你的意思，但我在這裡陪你。你可以多說一點嗎？",
            "action": "NONE"
        }

    # --- 步驟 D: 回傳訊息 ---
    try:
        reply_message = get_reply_object(matched_intent["response"], matched_intent["action"])
        
        line_bot_api.reply_message(
            event.reply_token,
            reply_message
        )
        print("✅ 回傳成功！")
    except LineBotApiError as e:
        print(f"❌ 回傳失敗: {e.status_code} {e.message}")