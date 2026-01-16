import os
from google import genai
from dotenv import load_dotenv

# 確保環境變數被載入
load_dotenv()

class AIClient:
    def __init__(self):
        self.client = None
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
                print("✅ AI Client 初始化成功")
            else:
                print("⚠️ 警告: 未設定 GEMINI_API_KEY")
        except Exception as e:
            print(f"❌ AI 初始化失敗: {e}")

    def polish_response(self, user_text, base_response, category):
        """
        呼叫 Gemini 潤飾回應
        """
        if not self.client:
            return base_response

        try:
            prompt = f"""
            你是一位溫暖的心理諮詢師助手。
            【情境】使用者說：「{user_text}」，分類為：「{category}」
            【任務】請將標準回覆：「{base_response}」改寫得更溫柔、有同理心。
            【規定】1.保留具體建議與按鈕指示。 2.字數100字內。
            """

            response = self.client.models.generate_content(
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

# 建立一個全域的實例供外部使用
ai_service = AIClient()