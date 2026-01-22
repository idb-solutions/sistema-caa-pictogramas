"""
__init__.py
Factory da aplicação Flask
Sistema de Comunicação Alternativa com Pictogramas para TEA
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app