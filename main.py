# importing required modules
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
# setting up Flask and linking to database
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
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
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
# helper function to query database for all blogs
def get_blogs():
    return Blog.query.all()

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    # setting my errors to nothing
    title_error = ''
    body_error = ''
    # using a conditional -- if method is POST that means user has put information into form; if GET the page will render as the blank form
    if request.method == 'POST':
        new_blog_title = request.form['blog-title']
        new_blog_body = request.form['blog-body']
        owner = User.query.filter_by(email=session['email']).first()
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

@app.route('/')
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    # getting id parameter from GET request, if there is an id parameter
    blog_id = request.args.get('id')
    # conditional returning just the posting if there is an id parameter
    if blog_id != None:
        blog_object = Blog.query.get(blog_id)
        title = blog_object.title
        body = blog_object.body
        return render_template('posting.html', title=title, body=body)
    # returning just the main page template
    else:
        return render_template('blog.html', title="Build a Blog", bloglist=get_blogs())

# makin that shit run!
if __name__ == '__main__':
    app.run()