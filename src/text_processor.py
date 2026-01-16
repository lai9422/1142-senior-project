import os
import jieba

# ==========================================
# 初始化設定 (只會執行一次)
# ==========================================

# 1. 載入自訂詞典 (如果檔案存在)
dict_path = 'mydict.txt'
if os.path.exists(dict_path):
    jieba.load_userdict(dict_path)
    print(f"✅ 已載入自訂詞典: {dict_path}")

# 2. 載入停用詞 (如果檔案存在)
del_words_path = 'delete_words.txt'
del_words_set = set()

if os.path.exists(del_words_path):
    with open(del_words_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            # 去除換行符號並加入集合
            word = line.strip()
            if word:
                del_words_set.add(word)
    print(f"✅ 已載入停用詞庫，共 {len(del_words_set)} 個詞")

# ==========================================
# 斷詞功能函式
# ==========================================
def segment_text(text):
    """
    對輸入文字進行斷詞，並過濾停用詞
    """
    # 精確模式斷詞
    raw_words = jieba.cut(text, cut_all=False)
    
    # 過濾停用詞與過短的詞 (選擇性保留長度 > 1 的詞，可依需求調整)
    filtered_words = []
    for word in raw_words:
        # 邏輯：詞不在停用詞清單中 且 (詞長度大於1 或 詞本身是重要的單字)
        if word not in del_words_set and word.strip() != '':
            filtered_words.append(word)
            
    print(f"✂️ 斷詞結果: {filtered_words}")
    return filtered_words