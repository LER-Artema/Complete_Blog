from datetime import date
from functools import wraps
from flask import Flask, render_template, redirect, url_for, abort, request, send_file
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
from forms import CreatePostForm, RegisterForm, LoginForm, CommentPostForm
import os
from dotenv import load_dotenv
import time
# from pathlib import Path
from nbconvert import HTMLExporter
import jinja2


# Authentication Function
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        try:
            if current_user.id != 1:
                return abort(403)
        except:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# inicialización de la aplicación y sus extensiones
load_dotenv('/Users/Artema/Desktop/my_envs/my_envs.env')
login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAX_CONTENT_PATH'] = 10000000
app.config['FLASK_DEBUG'] = 0


ckeditor = CKEditor(app)
Bootstrap(app)
login_manager.init_app(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False,
                    use_ssl=False,
                    base_url=None)

# vínculo a la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# inicialización de la aplicación de usuario
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# definición de tablas 
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    author_id = db.Column(db.Integer(), ForeignKey('users.id'), nullable=False)

    id = db.Column(db.Integer, primary_key=True)
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # file = db.Column(db.String(250), unique=True, nullable=False)

    comments = relationship("Comments", back_populates='blog_post')


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comments = db.Column(db.String(500), nullable=False)
    comment_author = relationship("User", back_populates='comments')
    blog_post = relationship("BlogPost", back_populates='comments')

    author_id = db.Column(db.Integer(), ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    # This will act like a List of BlogPost objects attached to each User.
    # lista de blog post objects vinculada al usuario
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comments", back_populates="comment_author")


class Notebook(db.Model):
    __tablename__ = "jupyter_notebooks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    file = db.Column(db.String(250), unique=False, nullable=False)


db.create_all()


@app.route('/')
def get_all_notebooks():
    # image = 'img/Funtionality Icons/IMG_9674.JPG'
    # image = 'img/Funtionality Icons/Frey Raiden.png'
    image = 'img/Funtionality Icons/Speech.JPG'

    notebooks = Notebook.query.all()
    admin = None
    if current_user.is_authenticated and current_user.id == 1:
        admin = True

    return render_template("index.html", all_posts=notebooks, current_user=current_user, image=image, admin=admin)


# Ruta original del blogpost
# @app.route('/')
# def get_all_notebooks():
#     image = 'img/Funtionality Icons/IMG_9674.JPG'
#     # image = 'img/Funtionality Icons/Frey Raiden.png'
#     image = 'img/Funtionality Icons/Speech.JPG'
#
#     posts = BlogPost.query.all()
#     admin = None
#     if current_user.is_authenticated and current_user.id == 1:
#         admin = True
#
#     return render_template("index.html", all_posts=posts, current_user=current_user, image=image, admin=admin)
#
@app.route('/upload_notebook', methods=['GET', 'POST'])
def upload_notebook():
    image = 'img/Funtionality Icons/Snake.jpg'
    admin = None
    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    if request.method == 'POST':
        f = request.files['file']
        f.filename = f.filename.replace('(', '')
        f.filename = f.filename.replace(')', '')

        directory = 'templates/projects/notebooks/'
        directory_html = 'templates/projects/html_notebooks/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(directory_html):
            os.makedirs(directory_html)

        f.save(os.path.join(directory, f.filename))


        name = str(f.filename).split('.ipynb')[0] + '.html'
        title = request.form['title']

        notebook = Notebook(
            title=title,
            file=name,
        )
        db.session.add(notebook)
        db.session.commit()
        import nbformat
        # from nbconvert.preprocessors import ExecutePreprocessor

        # read source notebook
        with open(f'templates/projects/notebooks/{f.filename}') as f:
            nb = nbformat.read(f, as_version=4)

        # execute notebook
        # ep = ExecutePreprocessor(timeout=-1, kernel_name='python3')
        # ep.preprocess(nb)

        # export to html
        html_exporter = HTMLExporter()
        html_exporter.exclude_input = False
        html_data, resources = html_exporter.from_notebook_node(nb)

        # write to output file
        with open(f"templates/projects/html_notebooks/{name}", "w",) as r:
            r.write(html_data)


        # Path(f"templates/projects/notebooks/{name}").rename(f"templates/projects/html_notebooks/{name}")

        time.sleep(5)

        return redirect(url_for('get_all_notebooks'))

    return render_template("upload_notebook.html", image=image, admin=admin)


@app.route('/download/<int:notebook>')
def download(notebook):
    requested_notebook = Notebook.query.get(notebook)
    jp_notebook = str(requested_notebook.file).strip('.html')
    return send_file(f'templates/projects/notebooks/{jp_notebook}.ipynb', as_attachment=True)


@app.route("/delete/<int:notebook_id>")
# @admin_only
def delete_post(notebook_id):
    admin = None

    try:
        if current_user.is_authenticated and current_user.id == 1:
            admin = True
    except:
        pass
    if admin:
        import os, shutil
        notebook_to_delete = Notebook.query.get(notebook_id)
        notebook_html_file = notebook_to_delete.file
        notebook_file = (notebook_to_delete.file).split('.html')[0] + '.ipynb'

        os.remove(f"templates/projects/html_notebooks/{notebook_html_file}")
        os.remove(f"templates/projects/notebooks/{notebook_file}")

        db.session.delete(notebook_to_delete)
        db.session.commit()
        # Path(f"templates/projects/notebooks/{name}").(f"templates/projects/html_notebooks/{name}")

        return redirect(url_for('get_all_notebooks'))
    else:
        # image = 'img/Funtionality Icons/Frey Raiden.png'

        return redirect(url_for('forbidden'))


@app.route("/about")
def about():
    image = 'img/Funtionality Icons/IMG_9674.JPG'
    admin = None
    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    return render_template("about.html", image=image, admin=admin)


@app.route('/register', methods=['GET', 'POST'])
def register():
    admin = None
    # image = 'img/Funtionality Icons/Ray Moded.jpeg'
    image = 'img/Funtionality Icons/RS.jpg'

    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    register_form = RegisterForm()
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        email_exists = User.query.filter(User.email == email).first()
        if email_exists == None:
            user = User(
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
                name=name
            )

            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('get_all_notebooks'))

        else:

            return render_template("register.html", form=register_form, image=image, admin=admin, email_error=True)

    return render_template("register.html", form=register_form, image=image, admin=admin)


@app.route("/forbidden")
def forbidden():
    image = 'img/Funtionality Icons/Frey Raiden.png'
    admin = False
    return render_template("denied.html", image=image, admin=admin)


@app.route("/contact")
def contact():
    # image = 'img/Funtionality Icons/MGS Full Image/IMG_9601.JPG'
    image = 'img/Funtionality Icons/Frey Raiden.png'

    admin = None
    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    return render_template("contact.html", image=image, admin=admin)


@app.route('/login', methods=['GET', 'POST'])
def login():
    admin = None
    image = 'img/Funtionality Icons/IMG_9640.JPG'
    if current_user.is_authenticated and current_user.id == 1:
        admin = True

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            # flash("That email does not exist, please try again.")
            return render_template("login.html", image=image, admin=admin, no_user=True)


        elif not check_password_hash(user.password, password):
            # flash('Incorrect Password, please try again.')
            return render_template("login.html", image=image, admin=admin, no_password=True)
        else:
            login_user(user)
            return redirect(url_for('get_all_notebooks'))

    return render_template("login.html", image=image, admin=admin)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_notebooks'))


# Ruta original de show posts
# @app.route("/post/<int:post_id>", methods=['GET', 'POST'])
# def show_post(post_id):
#     image = 'img/Funtionality Icons/Snake.jpg'
#     requested_post = BlogPost.query.get(post_id)
#     comments = Comments.query.all()
#
#     admin = None
#     if current_user.is_authenticated and current_user.id == 1:
#         admin = True
#     edit_form = CommentPostForm(
#         body=''
#     )
#     if edit_form.validate_on_submit():
#         if current_user.is_authenticated:
#             comment = Comments(comments=edit_form.body.data, comment_author=current_user)
#             db.session.add(comment)
#             db.session.commit()
#             return redirect(url_for('show_post', post_id=requested_post.id))
#         else:
#             flash("You need to login to submit a comment")
#             return redirect(url_for('login'))
#     return render_template("post.html", post=requested_post, image=image, admin=admin, form=edit_form,
#                            comments=comments)
#

@app.route("/new-post", methods=['GET', 'POST'])
@admin_only
def add_new_post():
    image = 'img/Funtionality Icons/Snake.jpg'
    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_notebooks"))
    return render_template("make-post.html", form=form, image=image, admin=admin)


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/post/<int:notebook_id>", methods=['GET', 'POST'])
def show_post(notebook_id):
    image = 'img/Funtionality Icons/Snake.jpg'
    requested_notebook = Notebook.query.get(notebook_id)

    admin = None
    if current_user.is_authenticated and current_user.id == 1:
        admin = True

    return render_template(f"projects/html_notebooks/{requested_notebook.file}", image=image, admin=admin)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)

# slategrey darksslategrey
# --jp-layout-color0 .jp-Cell

# A3A3A1--jp-layout-color0 .jp-Cell
