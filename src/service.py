# ==========================================
# 匯入必要的模組
# ==========================================
import os
import json
import jieba           # 中文斷詞
import mysql.connector # MySQL 資料庫
from google import genai     # Google GenAI 新版 SDK
from dotenv import load_dotenv # 讀取 .env 環境變數

# Line Bot SDK 相關
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction
)
from linebot.exceptions import LineBotApiError

# 專案內部匯入
from src.line_bot_api import line_bot_api, handler
from config import Config

# 確保環境變數被載入
load_dotenv()

# ==========================================
# 1. 初始化 AI Client (修正為新版寫法)
# ==========================================
client = None # 全域變數

try:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        # 新版 SDK 初始化：建立 Client 物件
        client = genai.Client(api_key=api_key)
        print("✅ AI Client 初始化成功")
    else:
        print("⚠️ 警告: 未設定 GEMINI_API_KEY，將無法使用 AI 潤飾功能")
except Exception as e:
    print(f"❌ AI 初始化失敗: {e}")

# ==========================================
# 2. 資料庫讀取函式 (含失敗備案)
# ==========================================
def get_intents():
    """
    從 MySQL 讀取意圖。若失敗則回傳備用資料。
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            connect_timeout=3
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bot_intents")
        rows = cursor.fetchall()

        intents = []
        for row in rows:
            # 解析 keywords JSON 字串
            if isinstance(row['keywords'], str):
                try:
                    row['keywords'] = json.loads(row['keywords'])
                except:
                    row['keywords'] = []
            intents.append(row)

        cursor.close()
        conn.close()

        if not intents:
            raise Exception("Database Empty")
        
        return intents

    except Exception as e:
        print(f"⚠️ 資料庫讀取失敗 ({e})，切換至備用資料")
        # 備用資料
        return [
            {
                "category": "緊急求助 (備用)",
                "keywords": ["死", "自殺", "頂樓"],
                "danger": 5,
                "response": "系統連線中，請先冷靜。我們很關心你，請撥打 113。",
                "action": "SHOW_CRISIS_MENU"
            },
            {
                "category": "打招呼 (備用)",
                "keywords": ["嗨", "你好"],
                "danger": 0,
                "response": "嗨！系統維護中，但我還是在這裡。",
                "action": "SHOW_MAIN_MENU"
            }
        ]

# ==========================================
# 3. AI 潤飾函式 (使用新版 SDK)
# ==========================================
def ai_polish_response(user_text, base_response, category):
    """
    呼叫 Gemini 潤飾回應
    """
    # 如果 Client 沒初始化成功，直接回傳原句
    if not client:
        return base_response

    try:
        # 提示詞 (Prompt)
        prompt = f"""
        你是一位溫暖的心理諮詢師助手。
        【情境】使用者說：「{user_text}」，分類為：「{category}」
        【任務】請將標準回覆：「{base_response}」改寫得更溫柔、有同理心。
        【規定】1.保留具體建議與按鈕指示。 2.字數100字內。
        """

        # 【修正重點】使用 client.models.generate_content
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        if response.text:
            return response.text.strip()
        else:
            return base_response

    except Exception as e:
        print(f"❌ AI 生成出錯: {e}")
        return base_response

# ==========================================
# 4. 輔助函式：產生回覆物件
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
# 5. Line Bot Handler
# ==========================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    print(f"📩 收到訊息: {user_msg}")

    # 1. 取得意圖庫
    intents = get_intents()

    # 2. 斷詞
    seg_list = list(jieba.cut(user_msg, cut_all=False))
    print(f"✂️ 斷詞: {seg_list}")

    # 3. 比對關鍵字
    found_intents = []
    for intent in intents:
        # 轉成 set 取交集
        if set(intent["keywords"]) & set(seg_list):
            found_intents.append(intent)

    # 4. 決策與 AI 潤飾
    final_response_text = ""
    action_code = "NONE"

    if found_intents:
        # 依危險度排序 (高 -> 低)
        found_intents.sort(key=lambda x: x["danger"], reverse=True)
        matched = found_intents[0]
        
        print(f"🎯 命中: {matched['category']}")
        
        # 呼叫 AI 潤飾
        final_response_text = ai_polish_response(
            user_msg, matched['response'], matched['category']
        )
        action_code = matched['action']
    else:
        # 未命中
        print("🤷‍♂️ 未命中，使用預設回應")
        default_text = "我不太確定你的意思，但我在這裡陪你。你可以多說一點嗎？"
        final_response_text = ai_polish_response(user_msg, default_text, "閒聊")
        action_code = "SHOW_MAIN_MENU"

    # 5. 回覆
    try:
        reply_obj = get_reply_object(final_response_text, action_code)
        line_bot_api.reply_message(event.reply_token, reply_obj)
        print("✅ 訊息已發送")
    except LineBotApiError as e:
        print(f"❌ Line API 錯誤: {e.status_code} {e.message}")