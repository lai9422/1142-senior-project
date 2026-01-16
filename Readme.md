# 程式架構
```
my_line_bot/
├── .env                  (維持不變)
├── run.py                (維持不變)
├── config.py             (維持不變)
├── mydict.txt            (新增: 自訂字典檔，選用)
├── delete_words.txt      (新增: 停用詞檔案，選用)
└── src/
    ├── __init__.py       (維持不變)
    ├── line_bot_api.py   (維持不變)
    ├── controller.py     (維持不變)
    ├── database.py       (🔥新: 專門處理資料庫)
    ├── ai_client.py      (🔥新: 專門處理 AI)
    ├── text_processor.py (🔥新: 專門處理斷詞與停用詞)
    ├── intent_matcher.py (🔥新: 專門處理關鍵字比對)
    └── service.py        (🔄修: 變成「指揮官」，負責調度上述模組)
```

# 函式安裝  
Anaconda Navigator
https://drive.google.com/file/d/1Wi1gUjaOv2A06M0gK8xqLiAIjOv1lbpD/view?usp=sharing

`pip install line-bot-sdk`

`pip install flask line-bot-sdk python-dotenv`

`"C:/Users/USER/AppData/Local/Programs/Python/Python313/python.exe" -m pip install flask`

`pip install jieba`

`pip install google-genai`

`pip install mysql-connector`

# 伺服器啟動
ngrok下載 https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip

金鑰設定
ngrok config add-authtoken 38H

ngrok http http://127.0.0.1:5001/

# 資料庫
密碼統一aeust

```
-- 1. 如果資料庫 'Aeust' 不存在，就建立它 (設定編碼為 utf8mb4 支援 Emoji)
CREATE DATABASE IF NOT EXISTS Aeust CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 切換到剛剛建立的資料庫
USE Aeust;

-- 3. 建立 'bot_intents' 資料表，用來存機器人的意圖與回覆
CREATE TABLE IF NOT EXISTS bot_intents (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '唯一編號 (自動遞增)',
    category VARCHAR(50) NOT NULL COMMENT '意圖分類 (例如：緊急求助)',
    keywords JSON NOT NULL COMMENT '關鍵字列表 (存成 JSON 陣列格式)',
    danger INT DEFAULT 0 COMMENT '危險指數 (0-5，越高越危險)',
    response TEXT NOT NULL COMMENT '機器人的標準回覆內容',
    action VARCHAR(50) DEFAULT 'NONE' COMMENT '後續動作代碼 (用來觸發按鈕)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '資料建立時間'
);

-- 4. 插入範例資料 (keywords 必須是 JSON 格式的字串)
INSERT INTO bot_intents (category, keywords, danger, response, action) VALUES 
(
    '緊急求助', 
    '["死", "自殺", "割腕", "消失", "頂樓"]', 
    5, 
    '同學，請先停下來，我們很重視你的安全。👇 請點擊下方按鈕，有人會馬上聽你說。', 
    'SHOW_CRISIS_MENU'
),
(
    '身體界線', 
    '["摸", "不舒服", "性騷擾"]', 
    3, 
    '這可能涉及性騷擾，你的感覺很重要。你想了解如何保護自己嗎？', 
    'LINK_LEGAL_INFO'
),
(
    '打招呼', 
    '["嗨", "你好", "哈囉"]', 
    0, 
    '嗨！我在這裡陪你，有什麼想說的嗎？', 
    'SHOW_MAIN_MENU'
);
```