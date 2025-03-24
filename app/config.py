class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Bb123321@localhost:5432/mybase'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'a7f1e9a2b0c5d4f8e3f9c7d1b4a0c9a6'  # Секретный ключ
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    # Добавляем настройки для CSRF защиты
    WTF_CSRF_ENABLED = True  # Включаем CSRF защиту
    WTF_CSRF_SECRET_KEY = 'a_random_csrf_secret_key'  # Генерируем секретный ключ для CSRF защиты
