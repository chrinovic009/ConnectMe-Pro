from app.utils.admin import blueprint
from app import db, UPLOAD_FOLDER, csrf, socketio
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func
from app.utils.authentication.models import Director, User, Notifications, Prediction
from app.utils.authentication.forms import CallingForm, Calling2Form
from app.utils.admin.models import Blog, Gallery, Partenaires, Team, Project
from app.utils.admin.forms import BlogForm, GalleryForm, PartnerForm, TeamForm, ProjectForm

# pour la page d'acceuil
@blueprint.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    compuny = Director.query.first()
    form = CallingForm()
    form_user = Calling2Form()
    notifs = Notifications.query.filter_by(is_read=False, user_id=current_user.id).order_by(Notifications.created_at.desc()).limit(5).all()

    preds = Prediction.query.order_by(Prediction.created_at.desc()).limit(3).all()
    print("Image URL:", compuny.image)

    return render_template('admin/profile.html', page_active="admin", 
                           compuny=compuny, form=form, form_user=form_user, 
                           notifs=notifs, preds=preds)

# site internet de connecteMe visibilite
@blueprint.route('/visibilite', methods=['POST', 'GET'])
@login_required
def visibilite():
    compuny = Director.query.first()

    form_blog = BlogForm()
    form_gallerie = GalleryForm()
    form_client = PartnerForm()
    form_teamer = TeamForm()
    form_proj = ProjectForm()
    
    myblog_post = Blog.query.order_by(Blog.created_at.desc()).limit(3).all()
    gallerie = Gallery.query.order_by(Gallery.created_at.desc()).limit(3).all()
    partenaire = Partenaires.query.limit(3).all()
    teamer = Team.query.order_by(Team.created_at.desc()).limit(3).all()
    projet = Project.query.order_by(Project.created_at.desc()).limit(3).all()

    return render_template('admin/visibilite.html', page_active="site_visibilite", 
                           compuny=compuny, myblog_post=myblog_post, form_blog=form_blog, 
                           form_gallerie=form_gallerie, form_client=form_client, gallerie=gallerie, 
                           partenaire=partenaire, form_teamer=form_teamer, teamer=teamer, form_proj=form_proj, projet=projet)
