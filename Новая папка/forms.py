from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FileField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length


class CharacterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    race = StringField('Race', validators=[DataRequired()])
    character_class = StringField('Class', validators=[DataRequired()])
    level = IntegerField('Level', validators=[DataRequired()])
    experience = IntegerField('Experience', validators=[DataRequired()])
    strength = IntegerField('Strength', validators=[DataRequired()])
    dexterity = IntegerField('Dexterity', validators=[DataRequired()])
    constitution = IntegerField('Constitution', validators=[DataRequired()])
    intelligence = IntegerField('Intelligence', validators=[DataRequired()])
    wisdom = IntegerField('Wisdom', validators=[DataRequired()])
    charisma = IntegerField('Charisma', validators=[DataRequired()])
    max_hp = IntegerField('Max HP', validators=[DataRequired()])
    current_hp = IntegerField('Current HP', validators=[DataRequired()])
    skills = TextAreaField('Skills', validators=[DataRequired()])
    description = TextAreaField('Description')
    image = FileField('Image')  # Поле для загрузки изображений


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Username must be between 3 and 100 characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    is_admin = BooleanField('Admin')  # Флажок для выбора роли администратора