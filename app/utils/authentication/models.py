from app import login_manager
from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

# Charge l'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class BirthdayMixin:
    birthdate = db.Column(db.Date)

    @property
    def age(self):
        today = datetime.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    @property 
    def birthdaysoon(self):
        today = datetime.today().date()
        birthday_this_year = self.birthdate.replace(year=today.year)
        birthday_next_year = self.birthdate.replace(year=today.year + 1)

        days_until_birthday = min(
            (birthday_this_year - today).days if birthday_this_year >= today else float('inf'),
            (birthday_next_year - today).days if birthday_this_year < today else float('inf')
        )

        return days_until_birthday == 3

    @property
    def is_birthday(self):
        today = datetime.today().date()
        birthdaythis_year = self.birthdate.replace(year=today.year)
        return birthdaythis_year == today

# Modèle utilisateur
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    compuny_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    position =  db.Column(db.String(255), nullable=False)
    docs = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(300), nullable=True)  # Photo officielle
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Chunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    # vector_id référence la position du vecteur dans l'index FAISS
    vector_id = db.Column(db.Integer, index=True)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Modèle pour les notifications client
class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # success, danger, warning, info
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)  # Ajout du champ de lecture

    def to_dict(self):
        """Convertir l'objet Notification en dictionnaire JSON"""
        return {
            "id": self.id,
            "type": self.type,
            "message": self.message,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": self.is_read
        }
