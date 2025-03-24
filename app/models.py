from datetime import datetime, timedelta
import random
from . import db  # db инициализирован в create_app

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Модель для категории продуктов
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Связь с продуктами
    products = db.relationship('Product', back_populates='category', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Category {self.name}>'

# Модель для продукта
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Связь с продажами
    sales = db.relationship('Sale', back_populates='product', lazy=True, cascade="all, delete-orphan")
    
    # Связь с категорией
    category = db.relationship('Category', back_populates='products')

    def __repr__(self):
        return f'<Product {self.name}>'

# Модель для продажи
class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    discount = db.Column(db.Float, nullable=True, default=0.0)

    # Связь с продуктом
    product = db.relationship('Product', back_populates='sales', foreign_keys=[product_id])

    def __repr__(self):
        return f'<Sale {self.product_id}, {self.quantity}>'

    @staticmethod
    def generate_random_sales(products):
        """Генерация случайных продаж за последние 6 месяцев с фильтрацией по дате"""
        for product in products:
            for _ in range(180):  # 180 дней (примерно 6 месяцев)
                random_date = datetime.utcnow() - timedelta(days=random.randint(0, 180))  # случайная дата в пределах 6 месяцев
                sale = Sale(
                    product_id=product.id,
                    quantity=random.randint(1, 10),  # случайное количество
                    sale_date=random_date,
                    discount=random.uniform(0, 0.5)  # случайная скидка от 0% до 50%
                )
                db.session.add(sale)
        db.session.commit()
