from flask import Flask
from src.controller import webhook_blueprint

def create_app():
    app = Flask(__name__)
    
    # 註冊 Blueprint (路由)
    app.register_blueprint(webhook_blueprint)
    
    return app