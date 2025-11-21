from app.utils.authentication import blueprint
from app import db, UPLOAD_FOLDER, csrf, socketio
from flask import render_template, flash, redirect, url_for, jsonify, request, send_from_directory, abort
from flask_login import login_required, current_user, login_user, logout_user
from app.utils.authentication.models import Director, User, Notifications
from app.utils.authentication.forms import LoginForm, RegistrationForm, EntrepriseForm
from app.utils.decorator.securite import save_file_to_cloudinary
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func
from app.utils.decorator.storage import upload_to_s3

# pour la page de login
@blueprint.route('/login', methods=["GET", "POST"])
def login():
    # Vérifier si l'entréprise existe
    existing_director = Director.query.first()
    if not existing_director:
        flash("Vous devez avoir une entréprise pour créer votre assistant.", "warning")
        return redirect(url_for('auth_blueprint.entreprise'))

    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for("home_blueprint.home"))

    form = LoginForm()

    if form.validate_on_submit():
        identifiant = form.email.data.strip().lower()  # champ unique (email ou username)

        # On essaie d'abord par email, sinon par username
        user = User.query.filter(
            (User.email == identifiant) | (User.username == identifiant)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Bienvenue {user.username}, authentification réussie !", "success")
            return redirect(url_for('home_blueprint.home'))
        else:
            flash("Email ou mot de passe incorrect", "danger")
            return redirect(url_for("auth_blueprint.login"))

    return render_template("authentication/sign-in.html", page_active="login", form=form, existing_director=existing_director)

# pour la page d'enregistrement
@blueprint.route('/register', methods=["GET", "POST"])
def register():
    existing_director = Director.query.first()
    if not existing_director:
        flash("Vous devez avoir une entréprise pour créer votre assistant.", "warning")
        return redirect(url_for('auth_blueprint.entreprise'))
    
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for("home_blueprint.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Vérifie si username/email déjà utilisés
        existing_username = User.query.filter_by(username=form.username.data.strip().lower()).first()
        existing_email = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if existing_username:
            flash("Ce nom d'utilisateur est déjà utilisé. Choisissez un autre.", "danger")
            return redirect(url_for("auth_blueprint.register"))

        if existing_email:
            flash("Cette adresse email est déjà utilisée. Choisissez une autre.", "danger")
            return redirect(url_for("auth_blueprint.register"))

        # Création utilisateur avec mot de passe hashé
        user = User(
            username=form.username.data.strip().lower(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)  # <--- bcrypt hash ici ✅

        db.session.add(user)
        db.session.commit()

        welcome_notification = Notifications(
            title="Nouveau abonné",
            user_id=existing_director.id,
            message=f"Un nommé {user.username} a créée un compte à {existing_director.compuny_name}",
            type="bi bi-info",
            created_at=datetime.now()
        )
        db.session.add(welcome_notification)
        db.session.commit()

        socketio.emit('new_notifications', {
            "id": welcome_notification.id,
            "message": welcome_notification.message,
            "type": welcome_notification.type,
            "date": welcome_notification.created_at.strftime("%d/%m/%Y %H:%M")
        }, namespace='/')

        flash("Votre compte a été créé avec succès !. Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for("auth_blueprint.login"))

    return render_template("authentication/sign-up.html", page_active="register", form=form, existing_director=existing_director)

@blueprint.route('/entreprise', methods=["GET", "POST"])
def entreprise():
    existing_director = Director.query.first()
    if existing_director:
        flash("Vous devez avoir une entréprise pour créer votre assistant.", "warning")
        return redirect(url_for('auth_blueprint.login'))
    
    form = EntrepriseForm()

    if form.validate_on_submit():

        image_url = None
        docs_url = None
        if form.image.data:
            image_url = save_file_to_cloudinary(form.image.data)

        if form.docs.data:
            docs_url = save_file_to_cloudinary(form.docs.data)

        # Création utilisateur avec mot de passe hashé
        user = User(
            username=form.username.data.strip().lower(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)  

        db.session.add(user)
        db.session.commit()
        
        director_profile = Director(
            user_id=user.id,
            username=form.username.data.strip(),
            email=form.email.data.strip(),
            compuny_name='ConnectMe',
            position='Administrateur',
            docs=docs_url,
            image=image_url
        )
        director_profile.set_password(form.password.data)
        db.session.add(director_profile)
        db.session.commit()

        # ⚠️ Attention: ici, il faut adapter car les fichiers ne sont plus dans static/
        pdf_path = os.path.join(UPLOAD_FOLDER, director_profile.docs)
        #add_pdf(pdf_path)

        #ensure_index_built(force=True)

        flash("Votre entréprise a été ajouté avec succès.", "info")
        return redirect(url_for('auth_blueprint.login'))
    
    return render_template("authentication/entreprise.html", page_active="entreprise", form=form)

@blueprint.route('/uploads/<filename>')
@login_required
def get_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename)