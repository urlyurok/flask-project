from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from . import db, cache
from .models import Category, Product, Sale
from .forms import CategoryForm, ProductForm
from faker import Faker
import random
from sqlalchemy import text  # Импортируем text для работы с текстовыми запросами SQL
from sqlalchemy.orm import joinedload

# Создаем blueprint
main = Blueprint('main', __name__, template_folder='templates')

def flash_message(message, category='success'):
    """Универсальная функция для отображения сообщений."""
    flash(message, category)

def commit_changes():
    """Функция для обработки commit и rollback."""
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash_message(f'Ошибка: {str(e)}', 'danger')

# Главная страница
@main.route('/')
def index():
    return render_template('index.html')

# --- Категории ---
@main.route('/categories')
def categories():
    categories_list = Category.query.all()
    return render_template('categories.html', categories=categories_list)

@main.route('/category/create', methods=['GET', 'POST'])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash_message('Категория с таким названием уже существует.', 'danger')
        else:
            category = Category(name=form.name.data)
            db.session.add(category)
            commit_changes()
            flash_message('Категория успешно создана!')
            return redirect(url_for('main.categories'))
    return render_template('create_category.html', form=form)

@main.route('/category/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)  # Передаем данные категории в форму

    # Если форма отправлена
    if form.validate_on_submit():
        category.name = form.name.data  # Обновляем имя категории
        commit_changes()  # Сохраняем изменения в базе данных
        flash_message('Категория успешно обновлена!')
        return redirect(url_for('main.categories'))

    return render_template('edit_category.html', form=form, category=category)


@main.route('/category/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)

    # Получаем все продукты из этой категории
    products_in_category = Product.query.filter_by(category_id=category.id).all()

    # Обновляем их категорию на None
    for product in products_in_category:
        product.category_id = None  # Теперь продукты не принадлежат категории
    db.session.commit()

    # Обновляем product_id в продажах на None
    sales_to_update = Sale.query.filter(Sale.product_id.in_([p.id for p in products_in_category])).all()
    for sale in sales_to_update:
        sale.product_id = None
    db.session.commit()

    # Удаляем продажи, у которых product_id теперь NULL
    db.session.execute(text("DELETE FROM sales WHERE product_id IS NULL"))
    db.session.commit()

    # Удаляем саму категорию
    db.session.delete(category)
    db.session.commit()

    flash('Категория успешно удалена!', 'success')
    return redirect(url_for('main.categories'))

# --- Продукты ---
@main.route('/products')
def products():
    products_list = Product.query.all()
    return render_template('products.html', products=products_list)

@main.route('/product/create', methods=['GET', 'POST'])
@main.route('/product/create', methods=['GET', 'POST'])
def create_product():
    form = ProductForm()
    form.category_id.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]

    if not form.category_id.choices:
        flash_message('Нет доступных категорий для выбора.', 'danger')
        return redirect(url_for('main.categories'))

    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            quantity=form.quantity.data,
            category_id=form.category_id.data
        )
        db.session.add(product)
        commit_changes()
        flash_message('Продукт успешно создан!')
        return redirect(url_for('main.products'))
    return render_template('create_product.html', form=form)


@main.route('/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)  # Ищем продукт по ID
    form = ProductForm(obj=product)  # Создаем форму и передаем в нее данные текущего продукта

    # Заполняем выпадающий список категорий
    form.category_id.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():  # Если форма прошла валидацию
        # Обновляем данные продукта из формы
        product.name = form.name.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.category_id = form.category_id.data

        # Сохраняем изменения в базе
        commit_changes()
        flash_message('Продукт успешно обновлен!')
        return redirect(url_for('main.products'))  # Перенаправляем на страницу с продуктами

    return render_template('edit_product.html', form=form, product=product)  # Отображаем форму редактирования


@main.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    # Находим продукт по ID
    product = Product.query.get(id)

    # Проверяем, существует ли продукт
    if product:
        # Удаляем все связанные продажи, которые ссылаются на этот продукт
        Sale.query.filter(Sale.product_id == product.id).delete()

        # Теперь удаляем сам продукт
        db.session.delete(product)
        commit_changes()

        # Сообщаем пользователю об успешном удалении
        flash_message('Продукт успешно удален!', 'success')
    else:
        # Если продукт не найден, показываем ошибку
        flash_message('Продукт не найден!', 'danger')

    # Перенаправляем пользователя обратно на страницу с продуктами
    return redirect(url_for('main.products'))

# --- Продажи ---
@main.route('/sales')
@cache.cached(timeout=60)
def sales():
    # Извлекаем продажи и подгружаем продукты с использованием joinedload
    sales_list = Sale.query.options(joinedload(Sale.product)).order_by(db.func.random()).all()

    # Вычисляем итоговую цену для каждой продажи
    for sale in sales_list:
        sale.total_price = sale.quantity * sale.product.price * (1 - sale.discount)

    return render_template('sales.html', sales=sales_list)

@main.route('/sale/create/<int:product_id>', methods=['GET', 'POST'])
def create_sale(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        try:
            quantity = int(request.form['quantity'])
            discount = float(request.form['discount'])

            if quantity <= 0 or discount < 0 or discount > 100:
                flash_message('Неверное значение количества или скидки.', 'danger')
                return redirect(url_for('main.create_sale', product_id=product_id))

            sale = Sale(product_id=product.id, quantity=quantity, discount=discount)
            db.session.add(sale)
            commit_changes()
            flash_message(f'Продажа для продукта {product.name} успешно создана!')
        except ValueError:
            flash_message('Неверный формат данных.', 'danger')
    return render_template('create_sale.html', product=product)

@main.route('/sale/edit/<int:sale_id>', methods=['GET', 'POST'])
def edit_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    if request.method == 'POST':
        try:
            sale.quantity = int(request.form['quantity'])
            sale.discount = float(request.form['discount'])

            if sale.quantity <= 0 or sale.discount < 0 or sale.discount > 100:
                flash_message('Неверное значение количества или скидки.', 'danger')
            else:
                commit_changes()
                flash_message('Продажа успешно обновлена!')
                return redirect(url_for('main.sales'))
        except ValueError:
            flash_message('Неверный формат данных.', 'danger')
    
    return render_template('edit_sale.html', sale=sale)


@main.route('/sale/delete/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)  # Ищем продажу по ID
    db.session.delete(sale)  # Удаляем продажу
    commit_changes()  # Сохраняем изменения в базе данных
    flash_message('Продажа успешно удалена!')  # Показываем сообщение
    return redirect(url_for('main.sales'))  # Перенаправляем на страницу с продажами


# --- Аналитика ---
@main.route('/api/sales/total')
@cache.cached(timeout=300)
def total_sales():
    total = db.session.query(db.func.sum(Sale.quantity * (Product.price - Product.price * Sale.discount))).scalar()
    return jsonify({'total_sales': total})

# Убираем дублирование маршрутов
@main.route('/top-products')
def top_products():
    # Запрос для получения топ-5 продуктов по количеству продаж и доходу
    top = db.session.query(
        Product.name,
        db.func.sum(Sale.quantity).label('total_quantity'),
        db.func.sum(Sale.quantity * (Product.price - Product.price * Sale.discount)).label('total_income')
    )\
    .join(Sale, Sale.product_id == Product.id)\
    .group_by(Product.id)\
    .order_by(db.func.sum(Sale.quantity).desc())\
    .limit(5).all()

    # Форматируем данные для шаблона
    top_products = []
    for product in top:
        top_products.append({
            'name': product.name,
            'total_quantity': product.total_quantity,
            'total_income': round(product.total_income, 2)  # Округляем доход до 2 знаков после запятой
        })

    # Отправляем данные в шаблон
    return render_template('top_products.html', top_products=top_products)

@main.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([{'id': product.id, 'name': product.name, 'price': product.price, 'quantity': product.quantity} for product in products])

@main.route('/generate-sales')
def generate_sales():
    fake = Faker()
    products = Product.query.all()
    for _ in range(100):
        product = random.choice(products)
        quantity = random.randint(1, 10)
        discount = random.uniform(0, 0.5)

        sale = Sale(
            product_id=product.id,
            quantity=quantity,
            discount=discount
        )
        db.session.add(sale)

    db.session.commit()
    flash_message('100 случайных продаж успешно добавлены!')
    return redirect(url_for('main.sales'))
