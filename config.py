import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

class Config:
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    PORT = os.getenv('PORT', 5001)

    # 保留你的檢查邏輯
    print("---------------------------------------------------")
    print(f"目前使用的 Token 長度: {len(LINE_CHANNEL_ACCESS_TOKEN)}")
    print(f"目前使用的 Token 前10碼: {LINE_CHANNEL_ACCESS_TOKEN[:10]}...")
    print("---------------------------------------------------")