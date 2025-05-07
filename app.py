from flask import Flask, request, redirect, url_for, flash, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lg-asphalt-secret-key'  # Temporary; will use .env later
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'  # For future extensions

# Initialize Bcrypt and LoginManager
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], role=user_data[2])
    return None

@app.route('/')
def home():
    return 'Welcome to LG Asphalt Project Management Platform!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Query user
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password, role FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and bcrypt.check_password_hash(user_data[2], password):
            user = User(id=user_data[0], username=user_data[1], role=user_data[3])
            login_user(user)
            return redirect(url_for('pm_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/pm')
@login_required
def pm_dashboard():
    return 'Welcome to the PM Dashboard (Admin Access)'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'

if __name__ == '__main__':
    app.run(debug=True)