# formulaire de l'application

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, FileField, TextAreaField, IntegerField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional

# formulaire pour les avis et les commentaires sur le site
class TestimonialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    role = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Content', validators=[DataRequired()])
    stars = IntegerField('Stars', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit Testimonial')

class BlogForm(FlaskForm):
    category = SelectField(
        'Category',
        choices=[
            ('Innovation Digitale', 'Innovation Digitale'),
            ('Design UX/UI', 'Design UX/UI'),
            ('Stratégie Numérique', 'Stratégie Numérique'),
            ('Transformation Digitale', 'Transformation Digitale'),
            ('Création de Contenu', 'Création de Contenu'),
            ('Développement Web', 'Développement Web'),
            ('Communication Visuelle', 'Communication Visuelle'),
            ('Collaboration Agile', 'Collaboration Agile'),
            ('Identité de Marque', 'Identité de Marque'),
            ('Expérience Utilisateur', 'Expérience Utilisateur'),
            ('Technologie & Créativité', 'Technologie & Créativité'),
            ('Électricité', 'Électricité'),
            ('Peinture', 'Peinture'),
        ],
        validators=[DataRequired()]
    )
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Add Post')

class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Send')

class GalleryForm(FlaskForm):
    category = SelectField(
        'Category',
        choices=[
            ('app', 'Fournitures'),
            ('product', 'Imprimérie'),
            ('branding', 'Services IT'),
            ('books', 'Génie Civil'),
        ],
        validators=[DataRequired()]
    )
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Add Post')

# Pour le directeur
class PartnerForm(FlaskForm):
    name = StringField('Name Partner', validators=[DataRequired(), Length(max=200)])
    link = StringField('Website Link', validators=[Optional(), Length(max=200)])
    image = FileField('Logo Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'svg'])])
    
    submit = SubmitField('Add Partner')

# Pour l'équipe
class TeamForm(FlaskForm):
    name = StringField('Name Partner', validators=[DataRequired(), Length(max=200)])
    poste = StringField('Position', validators=[DataRequired(), Length(max=200)])
    facebook = StringField('Facebook Link', validators=[Optional()])
    insta = StringField('Instagram Link', validators=[Optional()])
    linked = StringField('Website Link', validators=[Optional()])
    image = FileField('Logo Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'svg'])])
    
    submit = SubmitField('Add Teamer')

# Pour le projet
class ProjectForm(FlaskForm):
    name = StringField('Name Project', validators=[DataRequired(), Length(max=200)])
    category = StringField('Category', validators=[DataRequired(), Length(max=200)])
    client = StringField('Client', validators=[Optional()])
    url = StringField('Url', validators=[Optional()])
    details = TextAreaField('Detail', validators=[Optional()])
    image = FileField('Logo Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'svg'])])
    
    submit = SubmitField('Add Project')
