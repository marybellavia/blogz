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
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def get_blogs():
    return Blog.query.all()

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ''
    body_error = ''
    if request.method == 'POST':
        new_blog_title = request.form['blog-title']
        new_blog_body = request.form['blog-body']
        new_blog = Blog(new_blog_title, new_blog_body)

        if new_blog_title == '':
            title_error = 'Please fill in the title'
        if new_blog_body == '':
            body_error = 'Please fill in the body'
        else:
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            return redirect('./blog?id={0}'.format(new_blog_id))
    
    return render_template('newpost.html', title="Add a Blog Entry", title_error=title_error, body_error=body_error)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id != None:
        blog_object = Blog.query.get(blog_id)
        title = blog_object.title
        body = blog_object.body
        return render_template('posting.html', title=title, body=body)
    else:
        return render_template('blog.html', title="Build a Blog", bloglist=get_blogs())

@app.route('/', methods=['GET'])
def index():
    return render_template('blog.html', title="Build a Blog", bloglist=get_blogs())

if __name__ == '__main__':
    app.run()