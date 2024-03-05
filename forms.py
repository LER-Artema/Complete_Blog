from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email


##WTForm
class CreatePostForm(FlaskForm):
    # title = StringField("Blog Post Title", validators=[DataRequired()])
    # subtitle = StringField("Subtitle", validators=[DataRequired()])
    # img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("", validators=[DataRequired()])
    # submit = SubmitField("Submit Post")

class CommentPostForm(FlaskForm):
    body = CKEditorField('Make a comment', validators=[DataRequired()])
    submit = SubmitField("Comment Post")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")
