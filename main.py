from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'blogz'
db = SQLAlchemy(app)

# create db
class Blog(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(120), unique=True)
   body = db.Column(db.Text)
   date = db.Column(db.DateTime)
   owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

   def __init__(self, title, body, owner):
       self.title = title
       self.body = body
       self.date = datetime.utcnow()
       self.owner = owner

   def __repr__(self):
       return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('Must sign in or create and account', 'error')
        return redirect('/login')

@app.route('/', methods=["POST", "GET"])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, header='Blog Users') 

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'error')
            return redirect('/')

        elif user and user.password != password:
            flash('User password incorrect', 'error')
            return redirect('/login')
        
        else:
            flash('User does not have account, Please create account', 'error')

    return render_template('login.html')


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
    
        if not username:
            flash('Can not leave username blank', 'error')
            return redirect('/signup')
        elif not password:
            flash('Can not leave password blank', 'error')
            return redirect('/signup')
        elif password != verify:
            flash('Passwords do not match', 'error') 
            return redirect('/signup')   
        elif len(username)<3 or len(password)<3:
            flash('Username and password must be at least 3 characters', 'error')
            return redirect('/signup')  
        else:
            if not verify:
                flash('Do not leave verify blank', 'error')
                return redirect('/signup')    
    
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Loged In', 'error')
            return redirect('/') 
        else:
            flash('Duplicate username', 'error')
            return redirect('/signup')

    return render_template('signup.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if 'user' in request.args:
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        blogs_user = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', blogs=blogs_user, user=user)

    blogs = Blog.query.order_by("date desc").all()
    blog_id = request.args.get('id')
    if not blog_id:
        blog = Blog.query.filter_by()
        return render_template('blog.html',blogs=blogs)
    else:
        blog = Blog.query.get(blog_id)
        title = blog.title
        body = blog.body
        return render_template('/blog_post.html', title=title, body=body)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        
        if not title:
            flash('Please enter a Title', 'error')
            return redirect('/newpost')
        elif not body:
            flash('Please enter a Blog Body', 'error')
            return redirect('/newpost')    
        else:        
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
        return render_template('/blog_post.html',title=title, body=body)   
    return render_template('/newpost.html')  

@app.route('/logout')
def logout ():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
   app.run()