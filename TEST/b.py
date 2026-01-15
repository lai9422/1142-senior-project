from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ==========================================
# 請填入你的 Key (確保沒有多餘空白)
# ==========================================
access_token = 'EGLy/YJSQQuARXbOhzTCtC0m2tmykFefsdCVAuELB5aEgyhMxZSSkFnpL/gh7OG2/KAtaAgGZqpuR3gMQfNakO VyoaXELWHRz26EtlvmwPWCpjCRmDNbvTYdVydlevvD95k6QKXIqcwsNXN3SfL62AdB04t89/1O/w1cDnyilFU='
access_token = access_token.strip()
secret = '7213c2b7e307e0174d67fd8bb425334d'


# 【新增這行】印出來檢查長度！
print("---------------------------------------------------")
print(f"目前使用的 Token 長度: {len(access_token)}")
print(f"目前使用的 Token 前10碼: {access_token[:10]}...")
print("---------------------------------------------------")

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

@app.route("/", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        return '伺服器正常運作中！'

    if request.method == 'POST':
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        
        # 印出收到什麼，證明 LINE 有連進來
        print("收到 LINE 請求:", body)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("❌ 錯誤：Channel Secret 填錯了，或簽章驗證失敗")
            abort(400)
        except Exception as e:
            print(f"❌ 未知錯誤：{e}")
            abort(500)
        return 'OK'

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

if __name__ == "__main__":
    app.run(port=5001, debug=True)