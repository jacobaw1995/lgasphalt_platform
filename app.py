from flask import Flask, request, redirect, url_for, flash, render_template, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lg-asphalt-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role
        self._is_customer = False

    def get_id(self):
        return f"user_{self.id}"

class Customer(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self._is_customer = True

    def get_id(self):
        return f"customer_{self.id}"

@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")
    if user_id.startswith('user_'):
        user_id = user_id.replace('user_', '')
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            user = User(id=user_data[0], username=user_data[1], role=user_data[2])
            print(f"Loaded admin user: id={user.id}, username={user.username}, is_customer={user._is_customer}")
            return user
    elif user_id.startswith('customer_'):
        customer_id = user_id.replace('customer_', '')
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email FROM customers WHERE id = ?', (customer_id,))
        customer_data = cursor.fetchone()
        conn.close()
        if customer_data:
            customer = Customer(id=customer_data[0], name=customer_data[1], email=customer_data[2])
            print(f"Loaded customer: id={customer.id}, name={customer.name}, is_customer={customer._is_customer}")
            return customer
    print("No user found for ID")
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return 'Welcome to LG Asphalt Project Management Platform!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password, role FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data and bcrypt.check_password_hash(user_data[2], password):
            user = User(id=user_data[0], username=user_data[1], role=user_data[3])
            login_user(user)
            print(f"Admin logged in: id={user.id}, username={user.username}")
            return redirect(url_for('pm_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, password FROM customers WHERE email = ?', (email,))
        customer_data = cursor.fetchone()
        conn.close()
        if customer_data and bcrypt.check_password_hash(customer_data[3], password):
            customer = Customer(id=customer_data[0], name=customer_data[1], email=customer_data[2])
            login_user(customer)
            print(f"Customer logged in: id={customer.id}, email={customer.email}")
            return redirect(url_for('customer_portal'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('customer_login'))
    return render_template('customer_portal.html')

@app.route('/customer_portal', methods=['GET', 'POST'])
@login_required
def customer_portal():
    if not hasattr(current_user, '_is_customer') or not current_user._is_customer:
        flash('Access restricted to customers.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, status, start_date, end_date FROM projects WHERE customer_id = ?', (current_user.id,))
    projects = [{'id': p[0], 'name': p[1], 'status': p[2], 'start_date': p[3], 'end_date': p[4]} for p in cursor.fetchall()]
    
    selected_project_id = request.form.get('project_id') or (projects[0]['id'] if projects else None)
    photos = []
    if selected_project_id:
        cursor.execute('SELECT id, filename, description, upload_date FROM photos WHERE project_id = ?', (selected_project_id,))
        photos = [{'id': p[0], 'filename': p[1], 'description': p[2], 'upload_date': p[3]} for p in cursor.fetchall()]
    
    conn.close()
    return render_template('customer_portal.html', projects=projects, photos=photos, selected_project_id=selected_project_id)

@app.route('/customer_logout')
@login_required
def customer_logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('customer_login'))

@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = bcrypt.generate_password_hash('default123').decode('utf-8')
        try:
            conn = sqlite3.connect('crm.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (name, email, phone, address, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, phone, address, password))
            conn.commit()
            conn.close()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('pm_dashboard'))
        except sqlite3.IntegrityError:
            flash('Error: Email already exists.', 'danger')
        except Exception as e:
            flash(f'Error adding customer: {str(e)}', 'danger')
    return render_template('add_customer.html')

@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM customers')
    customers = cursor.fetchall()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        estimate_num = request.form.get('estimate_num')
        status = request.form.get('status')
        asphalt_type = request.form.get('asphalt_type')
        square_footage = request.form.get('square_footage')
        thickness_inches = request.form.get('thickness_inches')
        start_date = request.form.get('start_date')
        due_date = request.form.get('due_date')
        project_address = request.form.get('project_address')
        try:
            cursor.execute('''
                INSERT INTO projects (customer_id, name, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer_id, estimate_num, status, start_date, due_date))
            conn.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('pm_dashboard'))
        except Exception as e:
            flash(f'Error adding project: {str(e)}', 'danger')
        finally:
            conn.close()
    return render_template('add_project.html', customers=customers)

@app.route('/project', methods=['GET'])
@app.route('/project/<int:project_id>')
@login_required
def project(project_id=None):
    if not project_id:
        project_id = request.args.get('project_id')
        if not project_id:
            flash('Please select a project.', 'danger')
            return redirect(url_for('pm_dashboard'))
    
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, customer_id, name, start_date, end_date, status FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if not project:
        conn.close()
        flash('Project not found.', 'danger')
        return redirect(url_for('pm_dashboard'))
    cursor.execute('SELECT id, name FROM customers WHERE id = ?', (project[1],))
    customer = cursor.fetchone()
    cursor.execute('SELECT id, type, category, amount, description, date FROM project_finances WHERE project_id = ?', (project_id,))
    finances = cursor.fetchall()
    cursor.execute('''
        SELECT t.id, t.description, t.status, t.start_date, t.end_date, t.duration_days, t.hours_spent, u.username
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        WHERE t.project_id = ?
    ''', (project_id,))
    tasks = cursor.fetchall()
    cursor.execute('SELECT id, filename, description, upload_date FROM photos WHERE project_id = ?', (project_id,))
    photos = [{'id': p[0], 'filename': p[1], 'description': p[2], 'upload_date': p[3]} for p in cursor.fetchall()]
    conn.close()
    project_dict = {
        'id': project[0],
        'customer_id': project[1],
        'name': project[2],
        'start_date': project[3],
        'end_date': project[4],
        'status': project[5]
    }
    customer_dict = {'id': customer[0], 'name': customer[1]}
    finances_list = [{'id': f[0], 'type': f[1], 'category': f[2], 'amount': f[3], 'description': f[4], 'date': f[5]} for f in finances]
    tasks_list = [{
        'id': t[0],
        'title': t[1],
        'status': t[2],
        'start_date': t[3],
        'due_date': t[4],
        'duration_days': t[5],
        'hours_spent': t[6],
        'assignee_username': t[7]
    } for t in tasks]
    return render_template('project.html', project=project_dict, customer=customer_dict, finances=finances_list, tasks=tasks_list, photos=photos)

@app.route('/project/<int:project_id>/add_finance', methods=['POST'])
@login_required
def add_finance(project_id):
    type = request.form.get('type')
    category = request.form.get('category')
    amount = request.form.get('amount')
    description = request.form.get('description')
    date = request.form.get('date')
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO project_finances (project_id, type, category, amount, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, type, category, amount, description, date))
        conn.commit()
        conn.close()
        flash('Finance entry added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding finance entry: {str(e)}', 'danger')
    return redirect(url_for('project', project_id=project_id))

@app.route('/project/<int:project_id>/add_task', methods=['GET', 'POST'])
@login_required
def add_task(project_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = [{'id': u[0], 'username': u[1]} for u in cursor.fetchall()]
    if request.method == 'POST':
        title = request.form.get('title')
        assignee = request.form.get('assignee') or None
        status = request.form.get('status')
        start_date = request.form.get('start_date') or None
        due_date = request.form.get('due_date') or None
        duration_days = request.form.get('duration_days') or None
        hours_spent = request.form.get('hours_spent') or None
        try:
            cursor.execute('''
                INSERT INTO tasks (project_id, description, assigned_to, status, start_date, end_date, duration_days, hours_spent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (project_id, title, assignee, status, start_date, due_date, duration_days, hours_spent))
            conn.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('project', project_id=project_id))
        except Exception as e:
            flash(f'Error adding task: {str(e)}', 'danger')
        finally:
            conn.close()
    conn.close()
    return render_template('add_task.html', users=users, project_id=project_id)

@app.route('/project/<int:project_id>/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo(project_id):
    # Debug user state
    user_id = getattr(current_user, 'id', None)
    is_customer = getattr(current_user, '_is_customer', False)
    role = getattr(current_user, 'role', 'unknown')
    print(f"Upload photo access: user_id={user_id}, is_customer={is_customer}, role={role}")

    # Explicitly check user role from database if needed
    if user_id and not is_customer:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data and user_data[0] != 'admin':
            print(f"User {user_id} is not admin, redirecting to pm_dashboard")
            flash('Access restricted to admins.', 'danger')
            return redirect(url_for('pm_dashboard'))

    if is_customer:
        print(f"User {user_id} is customer, redirecting to customer_portal")
        flash('Access restricted to admins.', 'danger')
        return redirect(url_for('customer_portal'))

    # Verify project exists
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    if not project:
        print(f"Project {project_id} not found, redirecting to pm_dashboard")
        flash('Project not found.', 'danger')
        return redirect(url_for('pm_dashboard'))

    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            description = request.form.get('description')
            upload_date = datetime.now().strftime('%Y-%m-%d')
            try:
                conn = sqlite3.connect('crm.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO photos (project_id, filename, description, upload_date)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, unique_filename, description, upload_date))
                conn.commit()
                conn.close()
                flash('Photo uploaded successfully!', 'success')
                return redirect(url_for('project', project_id=project_id))
            except Exception as e:
                flash(f'Error uploading photo: {str(e)}', 'danger')
        else:
            flash('Invalid file type. Allowed: png, jpg, jpeg, gif.', 'danger')
    return render_template('upload_photo.html', project_id=project_id)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/pm')
@login_required
def pm_dashboard():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, start_date, end_date, status FROM projects')
    projects = [{'id': p[0], 'name': p[1], 'start_date': p[2], 'end_date': p[3], 'status': p[4]} for p in cursor.fetchall()]
    conn.close()
    return render_template('dashboard.html', projects=projects)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)