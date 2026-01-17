from flask import Blueprint, render_template, request, redirect, url_for
from src.database import (
    get_intents, update_keywords_in_db, insert_new_category, 
    get_all_modifiers, add_modifier, delete_modifier 
)
from src.text_processor import analyze_folder_words

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/admin', methods=['GET'])
def admin_dashboard():
    # 1. 取得意圖
    intents = get_intents()
    # 2. 分析文章
    top_words = analyze_folder_words(folder_path='./files', top_n=30)
    # 3. (新) 取得修飾語
    modifiers = get_all_modifiers()
    
    return render_template('admin.html', intents=intents, top_words=top_words, modifiers=modifiers)

@admin_blueprint.route('/admin/submit', methods=['POST'])
def admin_submit():
    selected_words = request.form.getlist('selected_words')
    mode = request.form.get('mode') 
    
    if mode == 'existing':
        cat_id = request.form.get('category_id')
        if selected_words: update_keywords_in_db(cat_id, selected_words)
    elif mode == 'new':
        new_cat = request.form.get('new_category_name')
        danger = request.form.get('danger_level')
        response = request.form.get('response_text')
        action = request.form.get('action_code')
        if new_cat: insert_new_category(new_cat, int(danger), response, action, selected_words)

    return redirect(url_for('admin.admin_dashboard'))

# ==========================
# 新增：處理修飾語的路由
# ==========================
@admin_blueprint.route('/admin/modifier/add', methods=['POST'])
def add_modifier_route():
    category = request.form.get('category')
    mod_type = request.form.get('mod_type')
    content = request.form.get('content')
    if category and mod_type and content:
        add_modifier(category, mod_type, content)
    return redirect(url_for('admin.admin_dashboard'))

@admin_blueprint.route('/admin/modifier/delete', methods=['POST'])
def delete_modifier_route():
    mod_id = request.form.get('mod_id')
    if mod_id:
        delete_modifier(mod_id)
    return redirect(url_for('admin.admin_dashboard'))