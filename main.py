from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)



# create db
class Blog(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(120), unique=True)
   body = db.Column(db.Text)
   date = db.Column(db.DateTime)

   def __init__(self, title):
       self.title = title
       self.date = datetime.utcnow()

   def __repr__(self):
       return '<Blog %r>' % self.title



@app.route('/posts', methods=['GET'])
def get_posts():
   return Blog.query.all()




# order post
@app.route('/get_ordered_posts', methods=['GET'])
def get_ordered_posts():
   return Blog.query.order_by("date desc").all()


# homepage
@app.route('/blog', methods=['GET'])
def blog():
   id = request.args.get('id', None)

   if id:
       post = Blog.query.filter_by(id=id).first()
       return render_template('posts.html', post=post)

   posts = get_ordered_posts()
   return render_template('blog.html', posts=posts)

@app.route('/')
def index():
    return redirect('/blog')


# Add new post
@app.route('/newpost', methods=['GET'])
def newpost():
   title = request.args.get('title', '')
   body = request.args.get('body', '')
   title_error = request.args.get('title_error', '')
   body_error = request.args.get('body_error', '')

   return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)


# Route after adding new post
@app.route('/post', methods=['POST'])
def post():
   title = request.form.get('title', '')
   body = request.form.get('body', '')
   title_error = request.form.get('title_error', '')
   body_error = request.form.get('body_error', '')

   # validation for empty values
   if not title or not body:
       if title == '':
           title_error = "Please provide a title"
       if body == '':
           body_error = "Please write your blog"
       return redirect(f'/newpost?title={title}&body={body}&title_error={title_error}&body_error={body_error}')

   # Add new post
   new_post = Blog(title)
   new_post.body = body
   db.session.add(new_post)
   db.session.commit()

   # Load the new post in an individual page
   id = new_post.id
   posts = Blog.query.filter_by(id=id).all()
   return render_template('blog.html', posts=posts)


if __name__ == '__main__':
   app.run()