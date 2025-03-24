from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, NumberRange

# Форма для категории
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Форма для категории
class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


# Форма для продукта
class ProductForm(FlaskForm):
    name = StringField('Название продукта', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired(), NumberRange(min=1, message="Цена должна быть положительной")])
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1, message="Количество должно быть хотя бы 1")])
    category_id = SelectField('Категория', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Добавить продукт')

# Форма для продажи
class SaleForm(FlaskForm):
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1, message="Количество должно быть хотя бы 1")])
    discount = FloatField('Скидка', validators=[DataRequired(), NumberRange(min=0, max=100, message="Скидка должна быть от 0 до 100")])
    submit = SubmitField('Создать продажу')
