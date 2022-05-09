from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    content = TextAreaField("Немного о себе", validators=[DataRequired()])
    submit = SubmitField('Оставить комментарий')
