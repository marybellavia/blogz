from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(120)) # TODO update this to be a longer amount of characters for blog content

    def __init__(self, title, content):
        self.title = title
        self.content = content

def get_blogs():
    return Blog.query.all()

@app.route('/add-blog', methods=['POST', 'GET'])
def add_blog():
    if request.method == 'POST':
        # TODO add error messages for if they leave either field blank

        new_blog_title = request.form['blog-title']
        new_blog_content = request.form['blog-content']
        new_blog = Blog(new_blog_title, new_blog_content)
        db.session.add(new_blog)
        db.session.commit()
        
        # TODO create redirect to new page displaying blog via blog id?

    
    return render_template('add-blog.html', title="Add a Blog Entry")

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    return render_template('blog.html', title="Build a Blog", bloglist=get_blogs())

@app.route('/', methods=['GET'])
def index():
    return render_template('blog.html', title="Build a Blog", bloglist=get_blogs())

if __name__ == '__main__':
    app.run()