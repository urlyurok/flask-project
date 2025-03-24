from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

# Инициализация объектов
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()

def create_app():
    app = Flask(__name__)

    # Устанавливаем секретный ключ
    app.config['SECRET_KEY'] = 'a7f1e9a2b0c5d4f8e3f9c7d1b4a0c9a6'
    
    # Загружаем конфигурацию из файла
    app.config.from_object('app.config.Config')

    # Инициализируем объекты
    db.init_app(app)  # Инициализируем базу данных
    migrate.init_app(app, db)  # Инициализируем миграции
    cache.init_app(app)  # Инициализируем кэш

    # Импортируем модели и маршруты
    from .models import Category, Product, Sale
    from .routes import main
    app.register_blueprint(main)

    return app
