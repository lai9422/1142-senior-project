# 程式架構
```my_line_bot/
├── .env                  # [新建] 放敏感資料 (Token, Secret)
├── run.py                # [新建] 程式啟動入口
├── config.py             # [新建] 讀取設定
└── src/                  # [新建] 原始碼資料夾
    ├── __init__.py       # 初始化 Flask App
    ├── line_bot_api.py   # 初始化 LINE API 與 Handler
    ├── controller.py     # 處理 Webhook 路由 (接收請求)
    └── service.py        # 處理訊息邏輯 (回覆訊息)
```

# 函式安裝
Anaconda Navigator
https://drive.google.com/file/d/1Wi1gUjaOv2A06M0gK8xqLiAIjOv1lbpD/view?usp=sharing

`pip install line-bot-sdk`

`pip install flask line-bot-sdk python-dotenv`

`"C:/Users/USER/AppData/Local/Programs/Python/Python313/python.exe" -m pip install flask`

# 伺服器啟動
ngrok下載 https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip

金鑰設定
ngrok config add-authtoken 38H

ngrok http http://127.0.0.1:5001/

