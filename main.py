# importing required modules
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
# setting up Flask, linking to database, setting secret key
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'thesmellofdogfartslingerintheair'
# creating Blog class to create database entries -- need title, body, owner
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
# creating User class to create database entries -- need username and password
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(255))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
# helper function to query database for all blogs
def get_all_blogs():
    return Blog.query.all()
# helper function to query database for all usernames
def get_all_usernames():
    return User.query.all()
# route to require login if you want to create a new blog post
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
# 
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ''
    password_error = ''
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        else:
            if not user:
                username_error = 'Username does not exist'
            elif not check_pw_hash(password, user.pw_hash):
                password_error = 'Username and password do not match.'

    return render_template('login.html', password_error=password_error, username_error=username_error, username=username)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''
    username = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = "A user with that username already exists!"
        elif verify != password:
            verify_error = "Those passwords don't match."
        elif username == '' or len(username) < 3:
            username_error = "You must enter a valid username (usernames must be more than 3 characters long)."
        elif password == '' or len(password) < 3:
            password_error = "You must enter a valid password (passwords must be more than 3 characters long)."
        elif not existing_user and verify == password:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error, username=username)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    # setting my errors to nothing
    title_error = ''
    body_error = ''
    # using a conditional -- if method is POST that means user has put information into form; if GET the page will render as the blank form
    if request.method == 'POST':
        new_blog_title = request.form['blog-title']
        new_blog_body = request.form['blog-body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(new_blog_title, new_blog_body, owner)
        # conditionals to insert error messages if the form is left blank
        if new_blog_title == '':
            title_error = 'Please fill in the title'
        if new_blog_body == '':
            body_error = 'Please fill in the body'
        # if form is filled out correctly this will add blog post to database and redirect to the new post
        else:
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            return redirect('./blog?id={0}'.format(new_blog_id))
    # returns the blank form on GET request
    return render_template('newpost.html', title="Add a Blog Entry", title_error=title_error, body_error=body_error)
# blog route; 
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    # grabbing id & user parameter from GET request, if present
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    # conditional returning just the posting if there is an id parameter
    if blog_id != None:
        blog_object = Blog.query.get(blog_id)
        title = blog_object.title
        body = blog_object.body
        owner_id = blog_object.owner_id
        user_object = User.query.get(owner_id)
        return render_template('blogpost.html', title=title, body=body, blog_object=blog_object, user_object=user_object)
    # conditional returning the list of posts by a specific username if there is a user parameter
    if user_id != None:
        user_object = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('userblogs.html', title='Blogz', bloglist=user_blogs, user_object=user_object)
    # returning just the main page template
    else:
        bloglist = get_all_blogs()
        userlist = get_all_usernames()
        return render_template('blog.html', title="Blogz", bloglist=bloglist, userlist=userlist)
# home/index route; lists all the usernames
@app.route('/')
def index():
    username_list = get_all_usernames()
    return render_template('index.html', username_list=username_list, title="Blogz")

# makin that shit run!
if __name__ == '__main__':
    app.run()