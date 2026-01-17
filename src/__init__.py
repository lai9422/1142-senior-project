from flask import Flask
from src.controller import webhook_blueprint
from src.admin import admin_blueprint  

def create_app():
    app = Flask(__name__)
    
    # 註冊 Blueprint (路由)
    app.register_blueprint(webhook_blueprint)
    
    return app

def create_app():
    app = Flask(__name__, template_folder='../templates') 
    
    # 註冊 Blueprints
    app.register_blueprint(webhook_blueprint)
    app.register_blueprint(admin_blueprint)
    
    return app