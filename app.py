from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# 1. INITIALIZE THE APP (This fixes your error)
app = Flask(__name__)
app.secret_key = "szabist_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # Using local sqlite for easy setup
db = SQLAlchemy(app)

# 2. DEFINE THE DATABASE MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(50))

class LoginAttempt(db.Model):
    username = db.Column(db.String(50), primary_key=True)
    attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)

# Create the database file automatically
with app.app_context():
    db.create_all()

# 3. DEFINE THE ROUTES
@app.route('/')
def home(): 
    return render_template('home.html')

@app.route('/about')
def about(): 
    return "<h1>About Us</h1><p>Welcome to our SZABIST project.</p>"

@app.route('/services')
def services(): 
    return "<h1>Our Services</h1><p>We provide web solutions.</p>"

@app.route('/contact')
def contact(): 
    return "<h1>Contact Us</h1><p>Contact: info@example.com</p>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            password=request.form['password'],
            full_name=request.form['full_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            city=request.form['city']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        
        attempt = LoginAttempt.query.get(uname)
        
        # Check if locked (30 min requirement)
        if attempt and attempt.locked_until and attempt.locked_until > datetime.now():
            time_left = attempt.locked_until - datetime.now()
            return f"Locked! Try again in {int(time_left.total_seconds() // 60)} minutes."

        user = User.query.filter_by(username=uname, password=pwd).first()
        
        if user:
            if attempt: db.session.delete(attempt)
            db.session.commit()
            return "<h1>Dashboard</h1><p>Login Successful!</p><a href='/all_users'>View All Users</a>"
        else:
            # Handle failed attempts
            if not attempt:
                attempt = LoginAttempt(username=uname, attempts=1)
                db.session.add(attempt)
            else:
                attempt.attempts += 1
                if attempt.attempts >= 5:
                    attempt.locked_until = datetime.now() + timedelta(minutes=30)
            db.session.commit()
            return "Invalid Credentials. <a href='/login'>Try again</a>"
            
    return render_template('login.html')

@app.route('/all_users')
def all_users():
    users = User.query.all()
    return render_template('all_users.html', users=users)

@app.route('/search', methods=['POST'])
def search():
    user_id = request.form['user_id']
    user = User.query.get(user_id)
    return render_template('details.html', user=user)

@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('all_users'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)