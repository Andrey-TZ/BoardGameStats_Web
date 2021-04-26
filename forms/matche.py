from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, RadioField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class NewMatch(FlaskForm):
    game = StringField('Название игры:', validators=[DataRequired()])
    result = RadioField('Результат:', validators=[DataRequired()],
                        choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    score = IntegerField("Количество очков, набранных вами:", validators=[DataRequired()])
