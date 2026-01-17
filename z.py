import mysql.connector

# 設定您的資料庫密碼 (請依實際情況修改)
DB_PWD = "aeust"  # 如果沒密碼請改成 ""

try:
    # 1. 先連線到 MySQL Server (不指定資料庫)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PWD
    )
    cursor = conn.cursor()
    
    # 2. 建立資料庫
    cursor.execute("CREATE DATABASE IF NOT EXISTS Aeust CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("✅ 資料庫 'Aeust' 檢查/建立成功")
    
    # 3. 選擇資料庫
    conn.database = "Aeust"
    
    # 4. 建立 bot_intents 表格
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_intents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            keywords JSON NOT NULL,
            danger INT DEFAULT 0,
            response TEXT NOT NULL,
            action VARCHAR(50) DEFAULT 'NONE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ 資料表 'bot_intents' 檢查/建立成功")

    # 5. 建立 response_modifiers 表格 (新功能)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS response_modifiers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            mod_type VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ 資料表 'response_modifiers' 檢查/建立成功")
    
    conn.close()
    print("🎉 資料庫初始化完成！")

except mysql.connector.Error as err:
    print(f"❌ 連線失敗: {err}")
    if "Access denied" in str(err):
        print("💡 提示: 密碼錯誤，請檢查 DB_PWD 變數或您的 MySQL 設定。")
    elif "Can't connect" in str(err):
        print("💡 提示: MySQL 服務沒開，請檢查 XAMPP。")