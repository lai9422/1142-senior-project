from flask import Blueprint, render_template, request, redirect, url_for
from src.database import get_intents, update_keywords_in_db, insert_new_category
from src.text_processor import analyze_folder_words

# 建立 Blueprint
admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/admin', methods=['GET'])
def admin_dashboard():
    # 1. 取得目前所有分類 (供下拉選單用)
    intents = get_intents()
    
    # 2. 分析文章詞頻
    top_words = analyze_folder_words(folder_path='./files', top_n=30)
    
    return render_template('admin.html', intents=intents, top_words=top_words)

@admin_blueprint.route('/admin/submit', methods=['POST'])
def admin_submit():
    # 1. 取得使用者勾選的詞
    selected_words = request.form.getlist('selected_words')
    
    if not selected_words:
        return "❌ 未選擇任何詞彙 <a href='/admin'>返回</a>"

    # 2. 判斷是「更新舊分類」還是「新分類」
    mode = request.form.get('mode') # 'existing' or 'new'
    
    if mode == 'existing':
        cat_id = request.form.get('category_id')
        update_keywords_in_db(cat_id, selected_words)
        
    elif mode == 'new':
        new_cat = request.form.get('new_category_name')
        danger = request.form.get('danger_level')
        response = request.form.get('response_text')
        action = request.form.get('action_code')
        
        insert_new_category(new_cat, int(danger), response, action, selected_words)

    return "✅ 更新成功！ <a href='/admin'>回到後台</a>"