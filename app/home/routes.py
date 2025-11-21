from app.utils.home import blueprint
from app import db, UPLOAD_FOLDER, csrf, socketio
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.utils.authentication.models import Director, User, Notifications
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func
from app.utils.admin.models import Testimonial, Partenaires, Team, Project, Gallery, Blog, Comment
from app.utils.admin.forms import TestimonialForm, CommentForm, BlogForm, GalleryForm, PartnerForm, TeamForm, ProjectForm
from app.utils.authentication.forms import CallingForm, Calling2Form
from app.utils.decorator.securite import save_file_to_cloudinary





# ---------------------------------------------------------------------------- pour les pages ----------------------------------------------------------------#
# pour la page d'acceuil
@blueprint.route('/')
def home():

    compuny = Director.query.first()

    return render_template('home/index.html', page_active="home", compuny=compuny)

# pour la page d'à propos
@blueprint.route('/about')
def about():
    compuny = Director.query.first()
    testimonials = Testimonial.query.all()
    partenaire = Partenaires.query.filter(Partenaires.image is not None).all()
    partenaire_all = Partenaires.query.all()
    teamer = Team.query.order_by(Team.created_at.desc()).all()
    projet = Project.query.order_by(Project.created_at.desc()).all()

    return render_template('home/about.html', page_active="about", 
                           compuny=compuny, testimonials=testimonials, 
                           partenaire=partenaire, partenaire_all=partenaire_all, 
                           teamer=teamer, projet=projet
                           )

# pour la page des services
@blueprint.route('/services')
def services():
    compuny = Director.query.first()
    # appel du formulaire de commentaires
    testimonial_form = TestimonialForm()

    return render_template('home/services.html', page_active="services", 
                           compuny=compuny, testimonial_form=testimonial_form
                           )

# pour la page de la gallerie
@blueprint.route('/portfolio')
def portfolio():
    compuny = Director.query.first()
    gallerie = Gallery.query.order_by(Gallery.created_at.desc()).all()

    return render_template('home/portfolio.html', page_active="portfolio", 
                           compuny=compuny, gallerie=gallerie
                           )

# pour la page d'équipe
@blueprint.route('/team')
def team():
    compuny = Director.query.first()
    teamer = Team.query.order_by(Team.created_at.desc()).all()

    return render_template('home/team.html', page_active="team", 
                           compuny=compuny, teamer=teamer
                           )

# pour la page du blog
@blueprint.route('/blog')
def blog():
    compuny = Director.query.first()
    myblog_post = Blog.query.order_by(Blog.created_at.desc()).all()
    
    return render_template('home/blog.html', page_active="blog", 
                           compuny=compuny, myblog_post=myblog_post
                           )

# pour la page de contact
@blueprint.route('/contact')
def contact():
    return render_template('home/contact.html', page_active="contact")

# --------------------------------------------------------------------------- pour les pages Fin --------------------------------------------------------------#





# ------------------------------------------------------------------------ pour les détails des pages ---------------------------------------------------------#

# pour le détail de la page de service
@blueprint.route('/services_details/<service>')
def services_details(service):
    compuny = Director.query.first()
    return render_template('home/services-details.html', page_active="services_details", 
                           compuny=compuny, service=service)

# pour le détail de la page de la gallerie
@blueprint.route('/portfolio_detail')
def portfolio_detail():
    compuny = Director.query.first()
    projet = Project.query.order_by(Project.created_at.desc()).first()
    projets = Project.query.order_by(Project.created_at.desc()).all()
    gallerie = Gallery.query.order_by(Gallery.created_at.desc()).all()

    return render_template('home/portfolio-details.html', page_active="portfolio_detail", 
                           compuny=compuny, projet=projet, projets=projets, gallerie=gallerie
                           )

# pour le détail de la page du blog
@blueprint.route('/blog_detail')
def blog_detail():
    compuny = Director.query.first()

    # pour le nuage de tags
    tag_count = db.session.query(Blog.category, db.func.count(Blog.id)).group_by(Blog.category).all()

    # Récupérer le dernier article publié
    latest_post = Blog.query.order_by(Blog.created_at.desc()).first()

    # Récupérer les autres articles pour "Recent Posts"
    recent_posts = Blog.query.order_by(Blog.created_at.desc()).limit(8).all()
    form_comments = CommentForm()

    # Récupérer le nombre d'articles par catégorie
    category_counts = db.session.query(Blog.category, func.count(Blog.id)).group_by(Blog.category).all()
    category_count_dict = {category: count for category, count in category_counts}

    # Récupérer les commentaires associés à cet article
    if latest_post:
        comments = Comment.query.filter_by(blog_id=latest_post.id).all()

        return render_template('home/blog-details.html', page_active="blog_detail",
                           compuny=compuny, tag_count=tag_count,
                           latest_post=latest_post, comments=comments,
                           recent_posts=recent_posts, form_comments=form_comments,
                           category_count_dict=category_count_dict
                           )

    return render_template('home/blog-details.html', page_active="blog_detail",
                           compuny=compuny, tag_count=tag_count,
                           latest_post=latest_post, recent_posts=recent_posts, 
                           form_comments=form_comments,
                           category_count_dict=category_count_dict
                           )

# ---------------------------------------------------------------------- pour les détails des pages Fin -------------------------------------------------------#





# ----------------------------------------------------------------------------- pour le support ---------------------------------------------------------------#

# pour la documentation
@blueprint.route('/document')
def document():
    compuny = Director.query.first()
    return render_template('home/document.html', page_active="document", compuny=compuny)

# pour l'aide
@blueprint.route('/aide')
def aide():
    compuny = Director.query.first()
    return render_template('home/aide.html', page_active="aide", compuny=compuny)

# --------------------------------------------------------------------------- pour le support Fin -------------------------------------------------------------#






# ------------------------------------------------------------------------ pour le formulaire -----------------------------------------------------------------#

# pour les temoignages
@blueprint.route('/comment_avis', methods=['POST', 'GET'])
def comment_avis():
    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial(
            name=form.name.data,
            role=form.role.data,
            content=form.content.data,
            stars=form.stars.data
        )
        
        db.session.add(testimonial)
        db.session.commit()
        flash('Votre commentaire nous ait parvenu avec succès!', 'success')
        return redirect(url_for('home_blueprint.services'))
    return redirect(url_for('home_blueprint.services'))

# route de commentaires du blog
@blueprint.route('/comment/<int:blog_id>', methods=['GET', 'POST'])
def comment_post(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    compuny = User.query.first()

    form_comments = CommentForm()
    if form_comments.validate_on_submit():
        new_comment = Comment(
            name=form_comments.name.data, email=form_comments.email.data,
            content=form_comments.content.data, user_id=current_user.id, blog_id=blog.id
        )
        
        db.session.add(new_comment)
        db.session.commit()

        welcome_notification = Notifications(
                title="Nouveau Commentaire",
                user_id=compuny.id,
                message=f"{new_comment.name} a commenté votre article {blog.title[:10]}... !",
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

    return redirect(request.referrer)

# --------------------------------------------------------------------- pour le formulaire Fin ---------------------------------------------------------------#




# ----------------------------------------------------------------- pour le formulaire de modification --------------------------------------------------------#
# pour la modification du nom administrateur
@blueprint.route('/modife', methods=["GET", "POST"])
@csrf.exempt 
def modife():
    # variable pour les informations de l'utilisateur
    user = User.query.filter_by(id=current_user.id).first()
    director = Director.query.filter_by(id=user.id).first()

    form_user = Calling2Form()

    if form_user.validate_on_submit():
        user = Director.query.get(director.id)

        if form_user.docs.data:
            user.docs = form_user.docs.data

        if user:
            user.user_id = user.user_id
            user.username = form_user.username.data
            user.email = user.email
            user.compuny_name = user.compuny_name
            user.position = user.position
            user.docs = user.docs
            user.password = user.password
            user.image = user.image

            db.session.commit()

            welcome_notification = Notifications(
                title="Mise à jour d'informations",
                user_id=user.id,
                message=f"Vous avez changé votre nom utilisateur en {user.username}",
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

            flash(f"Votre nom a été modifié avec succès! Desormé, l assistant vous appelera {user.username}", "success")
            return redirect(url_for('admin_blueprint.admin'))

    return redirect(url_for('admin_blueprint.admin'))

# route d'un new post
@blueprint.route('/new_post', methods=['POST', 'GET'])
def new_post():
    compuny = Director.query.first()

    form_blog = BlogForm()

    if form_blog.validate_on_submit():
        image_url = None
        if form_blog.image.data:
            image_url = save_file_to_cloudinary(form_blog.image.data)

            new_blog = Blog(
                user_id=compuny.id,
                auteur_name=compuny.username,
                auteur_names=compuny.compuny_name,
                auteur_image=compuny.image,
                category=form_blog.category.data,
                poste=compuny.position,
                title=form_blog.title.data,
                content=form_blog.content.data,
                image=image_url
            )
            db.session.add(new_blog)
            db.session.commit()

            welcome_notification = Notifications(
                title="Nouveau Blog",
                user_id=compuny.id,
                message=f"Vous avez ajouté {new_blog.title[:10]}... à votre blog !",
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

            flash("Poste ajouté avec succès !", "success")
            return redirect(url_for("admin_blueprint.admin"))

    return redirect(url_for("admin_blueprint.admin"))

# route d'un new gallerie
@blueprint.route('/new_gallerie', methods=['POST', 'GET'])
def new_gallerie():
    compuny = Director.query.first()

    form_gallerie = GalleryForm()

    if form_gallerie.validate_on_submit():
        image_url = None
        if form_gallerie.image.data:
            image_url = save_file_to_cloudinary(form_gallerie.image.data)

            new_galleries = Gallery(
                category=form_gallerie.category.data,
                title=form_gallerie.title.data,
                description=form_gallerie.description.data,
                image=image_url
            )
            db.session.add(new_galleries)
            db.session.commit()

            welcome_notification = Notifications(
                title="Nouvelle Photo",
                user_id=compuny.id,
                message=f"Vous avez ajouté {new_galleries.title[:10]}... à votre gallerie !",
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

            flash("Image ajoutée avec succès !", "success")
            return redirect(url_for("admin_blueprint.admin"))

    return redirect(url_for("admin_blueprint.admin"))

@blueprint.route('/new_client', methods=['GET', 'POST'])
def new_client():
    compuny = Director.query.first()
    form_client = PartnerForm()

    if form_client.validate_on_submit():

        image_url = None
        if form_client.image.data:
            image_url = save_file_to_cloudinary(form_client.image.data)

            partenaires = Partenaires(
                name=form_client.name.data,
                link=form_client.link.data,
                image=image_url
            )
            db.session.add(partenaires)
            db.session.commit()

            welcome_notification = Notifications(
                title="Nouveau Client",
                user_id=compuny.id,
                message=f"Vous avez ajouté le client {partenaires.name[:10]}... à votre liste de clients !",
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

            flash(f"Le client {partenaires.name} a été ajouté avec succès!", "success")
            return redirect(url_for("admin_blueprint.admin"))

    return redirect(url_for("admin_blueprint.admin"))

@blueprint.route('/new_teamer', methods=['GET', 'POST'])
def new_teamer():
    compuny = Director.query.first()
    form_teamer = TeamForm()

    if form_teamer.validate_on_submit():

        image_url = None
        if form_teamer.image.data:
            image_url = save_file_to_cloudinary(form_teamer.image.data)

            team_member = Team(
                name=form_teamer.name.data,
                poste=form_teamer.poste.data,
                facebook=form_teamer.facebook.data,
                insta=form_teamer.insta.data,
                linked=form_teamer.linked.data,
                image=image_url
            )
            db.session.add(team_member)
            db.session.commit()

            welcome_notification = Notifications(
                title="Nouveau Membre de l'Équipe",
                user_id=compuny.id,
                message=f"Vous avez ajouté {team_member.name} à l'équipe !",
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

            flash(f"Le membre de l'équipe {team_member.name} a été ajouté avec succès!", "success")
            return redirect(url_for("admin_blueprint.admin"))

    return redirect(url_for("admin_blueprint.admin"))

@blueprint.route('/new_project', methods=['GET', 'POST'])
def new_project():
    compuny = Director.query.first()
    form_teamer = ProjectForm()

    if form_teamer.validate_on_submit():

        image_url = None
        if form_teamer.image.data:
            image_url = save_file_to_cloudinary(form_teamer.image.data)

            team_member = Project(
                name=form_teamer.name.data,
                category=form_teamer.category.data,
                client=form_teamer.client.data,
                url=form_teamer.url.data,
                details=form_teamer.details.data,
                image=image_url,
            )
            db.session.add(team_member)
            db.session.commit()

            welcome_notification = Notifications(
                title="Nouveau Projet",
                user_id=compuny.id,
                message=f"Vous avez ajouté {team_member.name} à vos projets !",
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

            flash(f"Le membre de l'équipe {team_member.name} a été ajouté avec succès!", "success")
            return redirect(url_for("admin_blueprint.admin"))

    return redirect(url_for("admin_blueprint.admin"))

# pour la modification du nom client
@blueprint.route('/modif', methods=["GET", "POST"])
@csrf.exempt 
def modif():
    # variable pour les informations de l'utilisateur
    user = User.query.filter_by(id=current_user.id).first()

    form = CallingForm()

    if form.validate_on_submit():
        user = User.query.get(user.id)

        if user:
            user.username = form.username.data
            user.email = user.email
            user.password = user.password

            db.session.commit()

            welcome_notification = Notifications(
                title="Mise à jour d'informations",
                user_id=user.id,
                message=f"Vous avez changé votre nom utilisateur en {user.username}",
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

            flash(f"Votre nom a été modifié avec succès! Desormé, l'assistant vous appelera {user.username}", "success")
            return redirect(url_for('admin_blueprint.admin'))

    return redirect(url_for('admin_blueprint.admin'))

# ---------------------------------------------------------------------- pour le formulaire de modification Fin ------------------------------------------------#


# ----------------------------------------------------------------------- pour le formulaire de suppression --------------------------------------------------#

# route pour supprimer un client
@blueprint.route('/delete_client/<int:post_id>', methods=['POST'])
@csrf.exempt  # Désactive la protection CSRF pour cette route
def delete_client(post_id):

    # variable pour les informations de l'utilisateur
    compuny = Director.query.first()

    post = Partenaires.query.get(post_id)
    
    if not post:
        flash("Client non trouvé.", "danger")
        return redirect(url_for("admin_blueprint.visibilite"))
    
    # Supprimer tous les articles liés manuellement
    Partenaires.query.filter_by(id=post_id).delete()

    db.session.delete(post)
    db.session.commit()

    welcome_notification = Notifications(
            title="Suppression",
            user_id=compuny.id,
            message=f"Vous avez supprimé un client !",
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
    
    flash("Ce client a été supprimé avec succès", "success")
    return redirect(url_for("admin_blueprint.visibilite"))

# route pour supprimer un blog
@blueprint.route('/delete_blog/<int:post_id>', methods=['POST'])
@csrf.exempt  # Désactive la protection CSRF pour cette route
def delete_blog(post_id):

    # variable pour les informations de l'utilisateur
    compuny = Director.query.first()

    post = Blog.query.get(post_id)
    comment = Blog.query.get(post_id)
    
    if not post:
        flash("Post non trouvé.", "danger")
        return redirect(url_for("admin_blueprint.visibilite"))
    
    # Supprimer tous les articles liés manuellement
    Blog.query.filter_by(id=post_id).delete()
    Comment.query.filter_by(blog_id=post_id).delete()

    db.session.delete(post)
    db.session.commit()

    welcome_notification = Notifications(
            title="Suppression",
            user_id=compuny.id,
            message=f"Vous avez supprimé un post !",
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
    
    flash("Ce post a été supprimé avec succès!", "success")
    return redirect(url_for("admin_blueprint.visibilite"))

# route pour supprimer une image
@blueprint.route('/delete_image/<int:post_id>', methods=['POST'])
@csrf.exempt  # Désactive la protection CSRF pour cette route
def delete_image(post_id):

    # variable pour les informations de l'utilisateur
    compuny = Director.query.first()

    post = Gallery.query.get(post_id)
    
    if not post:
        flash("Image non trouvée.", "danger")
        return redirect(url_for("admin_blueprint.visibilite"))
    
    # Supprimer tous les articles liés manuellement
    Gallery.query.filter_by(id=post_id).delete()

    db.session.delete(post)
    db.session.commit()

    welcome_notification = Notifications(
            title="Suppression",
            user_id=compuny.id,
            message=f"Vous avez supprimé une image !",
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
    
    flash("Cette image a été supprimée avec succès!", "success")
    return redirect(url_for("admin_blueprint.visibilite"))

# route pour supprimer un membre
@blueprint.route('/delete_team/<int:post_id>', methods=['POST'])
@csrf.exempt  # Désactive la protection CSRF pour cette route
def delete_team(post_id):

    # variable pour les informations de l'utilisateur
    compuny = Director.query.first()

    post = Team.query.get(post_id)
    
    if not post:
        flash("Membre non trouvé.", "danger")
        return redirect(url_for("admin_blueprint.visibilite"))
    
    # Supprimer tous les articles liés manuellement
    Team.query.filter_by(id=post_id).delete()

    db.session.delete(post)
    db.session.commit()

    welcome_notification = Notifications(
            title="Suppression",
            user_id=compuny.id,
            message=f"Vous avez supprimé un membre à l'équipe !",
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
    
    flash("Ce membre a été supprimée avec succès!", "success")
    return redirect(url_for("admin_blueprint.visibilite"))

# route pour supprimer un projet
@blueprint.route('/delete_projet/<int:post_id>', methods=['POST'])
@csrf.exempt  # Désactive la protection CSRF pour cette route
def delete_projet(post_id):

    # variable pour les informations de l'utilisateur
    compuny = Director.query.first()

    post = Project.query.get(post_id)
    
    if not post:
        flash("Projet non trouvé.", "danger")
        return redirect(url_for("admin_blueprint.visibilite"))
    
    # Supprimer tous les articles liés manuellement
    Project.query.filter_by(id=post_id).delete()

    db.session.delete(post)
    db.session.commit()

    welcome_notification = Notifications(
            title="Suppression",
            user_id=compuny.id,
            message=f"Vous avez supprimé un projet!",
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
    
    flash("Ce membre a été supprimée avec succès!", "success")
    return redirect(url_for("admin_blueprint.visibilite"))

# --------------------------------------------------------------------- pour le formulaire de suppression Fin ------------------------------------------------#