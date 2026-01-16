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
# [src/database.py] 的最下方加入

def update_keywords_in_db(category_id, new_keywords):
    """ 更新現有分類的關鍵字 (讀取舊的 -> 合併 -> 寫回) """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)

        # 1. 查出舊的
        cursor.execute("SELECT keywords FROM bot_intents WHERE id = %s", (category_id,))
        row = cursor.fetchone()
        
        current_keywords = []
        if row and row['keywords']:
            # 判斷是字串還是已經是 list (視 driver 版本而定)
            if isinstance(row['keywords'], str):
                current_keywords = json.loads(row['keywords'])
            else:
                current_keywords = row['keywords']

        # 2. 合併 (使用 set 去重複)
        updated_set = set(current_keywords)
        for w in new_keywords:
            updated_set.add(w)
        
        final_json = json.dumps(list(updated_set), ensure_ascii=False)

        # 3. 更新
        cursor.execute("UPDATE bot_intents SET keywords = %s WHERE id = %s", (final_json, category_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB 更新錯誤: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def insert_new_category(category, danger, response, action, keywords):
    """ 插入全新的分類 """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        keywords_json = json.dumps(keywords, ensure_ascii=False)
        
        sql = """
        INSERT INTO bot_intents (category, danger, response, action, keywords)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (category, danger, response, action, keywords_json))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB 新增錯誤: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()