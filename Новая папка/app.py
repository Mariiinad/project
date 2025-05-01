import os
from random import choice, randint
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import CharacterForm, LoginForm, RegistrationForm

# Flask App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    skills = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)


# Routes
@app.route('/')
def index():
    characters = Character.query.all()
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
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)

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
            skills=form.skills.data,
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


if __name__ == '__main__':
    db.create_all()  # Сброс базы данных при запуске
    app.run(debug=True)