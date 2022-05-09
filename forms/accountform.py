from flask_wtf import FlaskForm
from wtforms import PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AccountForm(FlaskForm):
    about = TextAreaField("Немного о себе")
    password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить')
