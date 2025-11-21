from app import login_manager
from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

# pour les temoignages
class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    def __repr__(self):
        return f'Testimonial {self.name}, {self.stars} stars, {self.content}'

# Model pour le blog
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    auteur_name = db.Column(db.String(255), nullable=False) 
    auteur_names = db.Column(db.String(255), nullable=False)
    auteur_image = db.Column(db.String(255), nullable=False) 
    category = db.Column(db.String(255), nullable=False) 
    poste = db.Column(db.String(255), nullable=False) 
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments =  db.relationship('Comment', backref='blog', lazy=True) 

# Model pour les commentaires
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # Permet de lier une réponse à un commentaire
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

# Modèle pour la gallerie
class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False) 
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Modèle pour le client
class Partenaires(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, index=True)  # Nom du partenaire
    image = db.Column(db.String(300), nullable=True)  # Logo de la companie partenaire
    link = db.Column(db.String(20), nullable=False, index=True)  # site web
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Model pour l'équipe
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    poste = db.Column(db.String(255), nullable=False)
    facebook = db.Column(db.String(255), nullable=False)
    insta = db.Column(db.String(255), nullable=False) 
    linked = db.Column(db.String(255), nullable=False) 
    image = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Model pour les projet
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    client = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=True) 
    details = db.Column(db.String(255), nullable=False) 
    image = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
