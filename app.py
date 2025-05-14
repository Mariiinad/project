import os
from random import choice, randint
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
from forms import CharacterForm, LoginForm, RegistrationForm

# Flask App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'json'}

# Database initialization
db = SQLAlchemy(app)

# Flask-Login initialization
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    race = db.Column(db.String(50), nullable=False)
    character_class = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    strength = db.Column(db.Integer, nullable=False)
    dexterity = db.Column(db.Integer, nullable=False)
    constitution = db.Column(db.Integer, nullable=False)
    intelligence = db.Column(db.Integer, nullable=False)
    wisdom = db.Column(db.Integer, nullable=False)
    charisma = db.Column(db.Integer, nullable=False)
    max_hp = db.Column(db.Integer, nullable=False)
    current_hp = db.Column(db.Integer, nullable=False)
    skills = db.Column(db.Text, nullable=False)  # Сохраняем навыки как строку
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)  # Для пути к изображению


# Routes
@app.route('/')
def index():
    # Получаем параметры из запроса
    name = request.args.get('name')
    race = request.args.get('race')
    character_class = request.args.get('character_class')
    level = request.args.get('level', type=int)

    # Параметры сортировки
    sort_by = request.args.get('sort_by', 'name')  # По умолчанию сортировка по имени
    order = request.args.get('order', 'asc')  # По умолчанию по возрастанию

    # Начинаем с базового запроса
    query = Character.query

    # Применяем фильтры
    if name:
        query = query.filter(Character.name.ilike(f"%{name}%"))
    if race:
        query = query.filter(Character.race == race)
    if character_class:
        query = query.filter(Character.character_class == character_class)
    if level:
        query = query.filter(Character.level == level)

    # Применяем сортировку
    if sort_by == 'level':
        query = query.order_by(Character.level.desc() if order == 'desc' else Character.level.asc())
    elif sort_by == 'experience':
        query = query.order_by(Character.experience.desc() if order == 'desc' else Character.experience.asc())
    else:
        query = query.order_by(Character.name.desc() if order == 'desc' else Character.name.asc())

    # Выполняем запрос
    characters = query.all()
    return render_template('index.html', characters=characters)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_character():
    if not current_user.is_admin:
        flash('Only admins can create characters.', 'danger')
        return redirect(url_for('index'))
    form = CharacterForm()
    if form.validate_on_submit():
        # Сбор навыков
        selected_skills = []
        for skill in [
            'acrobatics', 'animal_handling', 'arcana', 'athletics', 'deception',
            'history', 'insight', 'intimidation', 'investigation', 'medicine',
            'nature', 'perception', 'performance', 'persuasion', 'religion',
            'sleight_of_hand', 'stealth', 'survival'
        ]:
            if getattr(form, skill).data:  # Проверяем, был ли выбран флажок
                selected_skills.append(skill.replace('_', ' ').title())

        # Преобразование навыков в строку для сохранения в базе данных
        skills_str = ', '.join(selected_skills)

        # Обработка изображения
        image_path = None
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                image_path = f"uploads/{filename}"

        # Создание персонажа
        character = Character(
            name=form.name.data,
            race=form.race.data,
            character_class=form.character_class.data,
            level=form.level.data,
            experience=form.experience.data,
            strength=form.strength.data,
            dexterity=form.dexterity.data,
            constitution=form.constitution.data,
            intelligence=form.intelligence.data,
            wisdom=form.wisdom.data,
            charisma=form.charisma.data,
            max_hp=form.max_hp.data,
            current_hp=form.current_hp.data,
            skills=skills_str,  # Сохраняем навыки как строку
            description=form.description.data,
            image_path=image_path
        )
        db.session.add(character)
        db.session.commit()
        flash('Character added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_character.html', form=form)


@app.route('/generate')
@login_required
def generate_character():
    if not current_user.is_admin:
        flash('Only admins can generate characters.', 'danger')
        return redirect(url_for('index'))

    races = ['Human', 'Elf', 'Dwarf', 'Halfling']
    classes = [
        'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk',
        'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard'
    ]
    skills = ['Acrobatics', 'Stealth', 'Persuasion', 'Athletics', 'Survival']

    max_hp = randint(10, 100)
    current_hp = randint(1, max_hp)

    character = Character(
        name=f"Random {choice(races)}",
        race=choice(races),
        character_class=choice(classes),
        level=randint(1, 20),
        experience=randint(0, 10000),
        strength=randint(8, 18),
        dexterity=randint(8, 18),
        constitution=randint(8, 18),
        intelligence=randint(8, 18),
        wisdom=randint(8, 18),
        charisma=randint(8, 18),
        max_hp=max_hp,
        current_hp=current_hp,
        skills=', '.join(choice(skills) for _ in range(3)),
        description="Generated character with random attributes."
    )
    db.session.add(character)
    db.session.commit()
    flash('Random character generated!', 'success')
    return redirect(url_for('index'))


@app.route('/character/<int:id>')
@login_required
def character_details(id):
    character = Character.query.get_or_404(id)
    return render_template('character_details.html', character=character)


@app.route('/download/<int:id>', methods=['GET'])
@login_required
def download_character(id):
    character = Character.query.get_or_404(id)
    if not character:
        flash('Character not found.', 'danger')
        return redirect(url_for('index'))

    # Формируем JSON-данные персонажа
    character_data = {
        "id": character.id,
        "name": character.name,
        "race": character.race,
        "character_class": character.character_class,
        "level": character.level,
        "experience": character.experience,
        "strength": character.strength,
        "dexterity": character.dexterity,
        "constitution": character.constitution,
        "intelligence": character.intelligence,
        "wisdom": character.wisdom,
        "charisma": character.charisma,
        "max_hp": character.max_hp,
        "current_hp": character.current_hp,
        "skills": character.skills,
        "description": character.description
    }

    # Сохранение JSON в файл
    filename = f"{character.name.replace(' ', '_')}.json"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(character_data, f, ensure_ascii=False, indent=4)

    # Отправка файла пользователю
    return send_file(filepath, as_attachment=True)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_character():
    if not current_user.is_admin:
        flash('Only admins can upload characters.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if file and file.filename.endswith('.json'):
            try:
                # Чтение содержимого файла
                data = json.load(file)

                # Проверка структуры JSON
                required_keys = {
                    "id", "name", "race", "character_class", "level", "experience",
                    "strength", "dexterity", "constitution", "intelligence",
                    "wisdom", "charisma", "max_hp", "current_hp", "skills", "description"
                }
                if not required_keys.issubset(data.keys()):
                    flash('Invalid JSON structure. Please upload a valid character file.', 'danger')
                    return redirect(request.url)

                # Добавление персонажа в базу данных
                character = Character(
                    name=data['name'],
                    race=data['race'],
                    character_class=data['character_class'],
                    level=data['level'],
                    experience=data['experience'],
                    strength=data['strength'],
                    dexterity=data['dexterity'],
                    constitution=data['constitution'],
                    intelligence=data['intelligence'],
                    wisdom=data['wisdom'],
                    charisma=data['charisma'],
                    max_hp=data['max_hp'],
                    current_hp=data['current_hp'],
                    skills=data['skills'],
                    description=data['description']
                )
                db.session.add(character)
                db.session.commit()
                flash('Character uploaded successfully!', 'success')
                return redirect(url_for('index'))
            except json.JSONDecodeError:
                flash('Invalid JSON file.', 'danger')
                return redirect(request.url)
        else:
            flash('Please upload a valid .json file.', 'danger')
            return redirect(request.url)

    return render_template('upload_character.html')


@app.route('/delete/<int:id>')
@login_required
def delete_character(id):
    if not current_user.is_admin:
        flash('Only admins can delete characters.', 'danger')
        return redirect(url_for('index'))
    character = Character.query.get_or_404(id)
    db.session.delete(character)
    db.session.commit()
    flash('Character deleted.', 'info')
    return redirect(url_for('index'))


@app.route('/edit/<int:character_id>', methods=['GET', 'POST'])
@login_required
def edit_character(character_id):
    if not current_user.is_admin:
        flash('Only admins can edit characters.', 'danger')
        return redirect(url_for('index'))

    character = Character.query.get_or_404(character_id)
    form = CharacterForm(obj=character)

    if form.validate_on_submit():
        # Обновление базовых полей
        character.name = form.name.data
        character.race = form.race.data
        character.character_class = form.character_class.data
        character.level = form.level.data
        character.experience = form.experience.data
        character.strength = form.strength.data
        character.dexterity = form.dexterity.data
        character.constitution = form.constitution.data
        character.intelligence = form.intelligence.data
        character.wisdom = form.wisdom.data
        character.charisma = form.charisma.data
        character.max_hp = form.max_hp.data
        character.current_hp = form.current_hp.data
        character.description = form.description.data

        # Обработка навыков
        selected_skills = []
        for skill in [
            'acrobatics', 'animal_handling', 'arcana', 'athletics', 'deception',
            'history', 'insight', 'intimidation', 'investigation', 'medicine',
            'nature', 'perception', 'performance', 'persuasion', 'religion',
            'sleight_of_hand', 'stealth', 'survival'
        ]:
            if getattr(form, skill).data:  # Проверяем выбран ли флажок
                selected_skills.append(skill.replace('_', ' ').title())

        # Обновление навыков в виде строки
        character.skills = ', '.join(selected_skills)

        # Обработка изображения
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                character.image_path = f"uploads/{filename}"

        db.session.commit()
        flash('Character updated successfully!', 'success')
        return redirect(url_for('index'))

    # Установить значения флажков для навыков
    if request.method == 'GET':
        skills_list = character.skills.split(', ') if character.skills else []
        for skill in skills_list:
            skill_field = skill.lower().replace(' ', '_')
            if hasattr(form, skill_field):
                getattr(form, skill_field).data = True

    return render_template('edit_character.html', form=form, character=character)


if __name__ == '__main__':
    db.create_all()  # Сброс базы данных при запуске
    app.run(debug=True)