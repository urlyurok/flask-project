from app import create_app, db
from app.models import Category, Product, Sale
import random

# Создаем экземпляр приложения
app = create_app()

# Эта часть выполняет добавление начальных данных, если таблицы пустые
def create_initial_data():
    with app.app_context():
        # Добавляем категории, если их нет в базе
        categories = ["Электроника", "Одежда", "Книги"]
        for cat_name in categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                db.session.add(category)
        db.session.commit()

        # Добавляем продукты, если их нет в базе
        products_data = {
            "Электроника": ["Ноутбук", "Смартфон", "Планшет", "Камера", "Наушники"],
            "Одежда": ["Футболка", "Джинсы", "Куртка", "Носки", "Кепка"],
            "Книги": ["Роман", "Научная книга", "Фэнтези", "Биография", "Комиксы"]
        }
        for category_name, products in products_data.items():
            category = Category.query.filter_by(name=category_name).first()
            for product_name in products:
                product = Product.query.filter_by(name=product_name, category_id=category.id).first()
                if not product:
                    product = Product(name=product_name, category_id=category.id, price=random.uniform(10, 100), quantity=random.randint(1, 100))
                    db.session.add(product)
        db.session.commit()

        # Добавляем продажи, если их нет в базе
        if not db.session.query(Sale).first():
            products = Product.query.all()
            Sale.generate_random_sales(products)

        print("Данные успешно добавлены!")

# Запуск приложения
if __name__ == "__main__":
    # Создаем начальные данные, если они отсутствуют
    create_initial_data()

    # Запускаем сервер
    app.run(debug=True)
