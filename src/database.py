import json
import mysql.connector
from config import Config

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
        return [
            {
                "category": "緊急求助 (備用)",
                "keywords": ["死", "自殺", "頂樓"],
                "danger": 5,
                "response": "1系統連線中，請先冷靜。我們很關心你，請撥打 113。",
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