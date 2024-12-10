from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math
import json

# Load configuration
with open('config.json', 'r') as c:
    params = json.load(c)['params']

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Configure database URI
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

# Define Models
class Contacts(db.Model):
    __tablename__ = 'contacts'
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    tagline = db.Column(db.String(120), nullable=False)

# Dashboard route
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Post.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')

        # Debugging: Print the received form data
        print(f"Received username: {username}")
        print(f"Received password: {userpass}")

        if username == params['admin_user'] and userpass == str(params['admin_pass']):
            session['user'] = username
            posts = Post.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
        else:
            return render_template('login.html', params=params, error="Invalid username or password!")

    return render_template('login.html', params=params)

# Edit route
@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()

            # Debugging: Print the received form data
            print(f"Received title: {box_title}")
            print(f"Received tagline: {tline}")
            print(f"Received slug: {slug}")
            print(f"Received content: {content}")

            if not all([box_title, tline, slug, content]):
                return "All fields are required!"

            if sno == '0':
                post = Post(title=box_title, slug=slug, content=content, tagline=tline, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno=sno).first()
                if post:
                    post.title = box_title
                    post.slug = slug
                    post.content = content
                    post.tagline = tline
                    post.date = date
                    db.session.commit()
            return redirect('/dashboard')

        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)
    return redirect('/dashboard')

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Post.query.filter_by(sno=sno).first()
        if post:
            db.session.delete(post)
            db.session.commit()
    return redirect('/dashboard')

@app.route("/")
def home():
    posts = Post.query.all()
    no_of_post = 2  # Setting default number of posts per page to 2 for testing
    last = math.ceil(len(posts) / no_of_post)
    page = request.args.get('page')
    if not str(page).isnumeric() or int(page) < 1:
        page = 1
    page = int(page)
    posts = posts[(page - 1) * no_of_post : page * no_of_post]

    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, phone=phone, mes=message, email=email, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

if __name__ == "__main__":
    app.run(debug=True, port=8001)
