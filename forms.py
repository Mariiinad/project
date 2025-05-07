from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed


class CharacterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    race = SelectField('Race', choices=[
        ('Human', 'Human'),
        ('Elf', 'Elf'),
        ('Dwarf', 'Dwarf'),
        ('Halfling', 'Halfling')
    ], validators=[DataRequired()])
    character_class = SelectField('Class', choices=[
        ('Barbarian', 'Barbarian'),
        ('Bard', 'Bard'),
        ('Cleric', 'Cleric'),
        ('Druid', 'Druid'),
        ('Fighter', 'Fighter'),
        ('Monk', 'Monk'),
        ('Paladin', 'Paladin'),
        ('Ranger', 'Ranger'),
        ('Rogue', 'Rogue'),
        ('Sorcerer', 'Sorcerer'),
        ('Warlock', 'Warlock'),
        ('Wizard', 'Wizard')
    ], validators=[DataRequired()])
    level = IntegerField('Level', validators=[DataRequired(), NumberRange(min=1, max=20)])
    experience = IntegerField('Experience', validators=[DataRequired()])
    strength = IntegerField('Strength', validators=[DataRequired(), NumberRange(min=8, max=20)])
    dexterity = IntegerField('Dexterity', validators=[DataRequired(), NumberRange(min=8, max=20)])
    constitution = IntegerField('Constitution', validators=[DataRequired(), NumberRange(min=8, max=20)])
    intelligence = IntegerField('Intelligence', validators=[DataRequired(), NumberRange(min=8, max=20)])
    wisdom = IntegerField('Wisdom', validators=[DataRequired(), NumberRange(min=8, max=20)])
    charisma = IntegerField('Charisma', validators=[DataRequired(), NumberRange(min=8, max=20)])
    max_hp = IntegerField('Max HP', validators=[DataRequired()])
    current_hp = IntegerField('Current HP', validators=[DataRequired()])

    # Навыки как отдельные BooleanField
    acrobatics = BooleanField('Acrobatics')
    animal_handling = BooleanField('Animal Handling')
    arcana = BooleanField('Arcana')
    athletics = BooleanField('Athletics')
    deception = BooleanField('Deception')
    history = BooleanField('History')
    insight = BooleanField('Insight')
    intimidation = BooleanField('Intimidation')
    investigation = BooleanField('Investigation')
    medicine = BooleanField('Medicine')
    nature = BooleanField('Nature')
    perception = BooleanField('Perception')
    performance = BooleanField('Performance')
    persuasion = BooleanField('Persuasion')
    religion = BooleanField('Religion')
    sleight_of_hand = BooleanField('Sleight of Hand')
    stealth = BooleanField('Stealth')
    survival = BooleanField('Survival')

    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')



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