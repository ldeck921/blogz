from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'df8f78dsa83mnk'


class Blog(db.Model):

    
    id = db.Column(db.Integer, primary_key=True)     
    title = db.Column(db.Text)  
    post = db.Column(db.Text)   
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post 
        self.owner = owner


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
    allowed_routes = ['login_user', 'show_blog', 'add_user', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    all_users = User.query.all()
    return render_template('index.html', list_all_users=all_users)


@app.route('/blogz')
def show_blog():
    post_id = request.args.get('id')
    single_user_id = request.args.get('owner_id')
    if (post_id):
        ind_post = Blog.query.filter_by(id=post_id)
        return render_template('individ_post.html', individ_post=ind_post)
    else:
        if (single_user_id):
            ind_user_blog_posts = Blog.query.filter_by(owner_id=single_user_id)
            return render_template('singleUser.html', posts=ind_user_blog_posts)
        else:
            all_blog_posts = Blog.query.all()
            return render_template('blog.html', posts=all_blog_posts)

def empty_val(x):
    if x:
        return True
    else:
        return False


@app.route('/newpost', methods=['POST', 'GET'])
def add_entry():

    if request.method == 'POST':

        post_title = request.form['blog_title']
        post_entry = request.form['blog_post']
        owner = User.query.filter_by(username=session['username']).first()
        post_new = Blog(post_title, post_entry, owner)

        if empty_val(post_title) and empty_val(post_entry):
            db.session.add(post_new)
            db.session.commit()
            post_link = "/blog?id=" + str(post_new.id)
            return redirect(post_link)
        else:
            if not empty_val(post_title) and not empty_val(post_entry):
                flash('Please enter a title and blog entry', 'error')
                return render_template('newpost.html', post_title=post_title, post_entry=post_entry)
            elif not empty_val(post_title):
                flash('Please enter a title', 'error')
                return render_template('newpost.html', post_entry=post_entry)
            elif not empty_val(post_entry):
                flash('Please enter a blog entry', 'error')
                return render_template('newpost.html', post_title=post_title)

    else:
        return render_template('newpost.html')


@app.route('/signup', methods=['POST', 'GET'])
def add_user():

    if request.method == 'POST':

        user_name = request.form['username']
        user_password = request.form['password']
        user_password_validate = request.form['password_validate']


        
        if not empty_val(user_name) or not empty_val(user_password) or not empty_val(user_password_validate):
            flash('All fields must be filled in', 'error')
            return render_template('signup.html')

        
        if user_password != user_password_validate:
            flash('Passwords must match', 'error')
            return render_template('signup.html')

        if len(user_password) < 3 and len(user_name) < 3:
            flash('Username and password must be at least three characters', 'error')
            return render_template('signup.html')

        if len(user_password) < 3:
            flash('Password must be at least three characters', 'error')
            return render_template('signup.html')

        if len(user_name) < 3:
            flash('Username must be at least three characters', 'error')
            return render_template('signup.html')

        
       
        existing_user = User.query.filter_by(username=user_name).first()
        
        if not existing_user: 
            user_new = User(user_name, user_password) 
            db.session.add(user_new)
            db.session.commit()
            session['username'] = user_name
            flash('New user created', 'success')
            return redirect('/newpost')
        else:
            flash('Error, there is an existing user with the same username', 'error')
            return render_template('signup.html')

    
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        if not username and not password:
            flash('Username and password cannot be blank', 'error')
            return render_template('login.html')
        if not username:
            flash('Username cannot be blank', 'error')
            return render_template('login.html')
        if not password:
            flash('Password cannot be blank', 'error')
            return render_template('login.html')
        
       
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username does not exist', 'error')
            return render_template('login.html')
        if user.password != password:
            flash('Password is incorrect', 'error')
            return render_template('login.html')

        
        if user and user.password == password:
            session['username'] = username
            return redirect('newpost')

    return render_template('login.html')
        
@app.route('/logout')
def logout():
    del session['username']
    flash('You are logged out', 'success')
    return redirect('/blog')


if __name__ == '__main__':
    app.run()