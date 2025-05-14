from flask import Flask, request, redirect, url_for, flash, render_template, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lg-asphalt-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['UPLOAD_FOLDER'] = 'Uploads'
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
            print(f"Loaded admin user: id={user.id}, username={user.username}, is_customer={user._is_customer}, role={user.role}")
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

def send_email(recipient_email, subject, body):
    try:
        # Load email configuration
        with open('email_config.txt', 'r') as f:
            config = dict(line.strip().split('=') for line in f if line.strip())
        sender_email = config['EMAIL_ADDRESS']
        password = config['EMAIL_PASSWORD']

        # Create the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Send the email via Gmail SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        flash(f"Failed to send email notification: {str(e)}", "warning")
        return False

@app.route('/send_test_email')
def send_test_email():
    recipient = "jacobaw1995@gmail.com"
    subject = "Test Email from LG Asphalt Platform"
    body = "This is a test email from the LG Asphalt Project Management Platform."
    print(f"Sending test email to {recipient}")
    send_email(recipient, subject, body)
    return "Test email sent. Check your inbox."

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
            print(f"Admin logged in: id={user.id}, username={user.username}, role={user.role}, is_customer={user._is_customer}")
            return redirect(url_for('pm_dashboard'))
        else:
            print(f"Admin login failed: username={username}")
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
            print(f"Customer logged in: id={customer.id}, email={customer.email}, is_customer={customer._is_customer}")
            return redirect(url_for('customer_portal'))
        else:
            print(f"Customer login failed: email={email}")
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
    print(f"Customer portal: user_id={current_user.id}, projects_fetched={len(projects)}")
    
    selected_project_id = request.form.get('project_id')
    if selected_project_id:
        try:
            selected_project_id = int(selected_project_id)
            cursor.execute('SELECT id FROM projects WHERE id = ? AND customer_id = ?', (selected_project_id, current_user.id))
            if not cursor.fetchone():
                selected_project_id = None
                print(f"Invalid project_id={selected_project_id} for user_id={current_user.id}")
        except ValueError:
            selected_project_id = None
            print(f"Invalid project_id format: {request.form.get('project_id')}")
    
    if not selected_project_id and projects:
        selected_project_id = projects[0]['id']
    
    photos = []
    if selected_project_id:
        cursor.execute('SELECT id, filename, description, upload_date FROM photos WHERE project_id = ?', (selected_project_id,))
        photos = [{'id': p[0], 'filename': p[1], 'description': p[2], 'upload_date': p[3]} for p in cursor.fetchall()]
        print(f"Customer portal: user_id={current_user.id}, selected_project_id={selected_project_id}, photos_fetched={len(photos)}")
    
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
    cursor.execute('SELECT id, customer_id, name, start_date, end_date, status, zip_code FROM projects WHERE id = ?', (project_id,))
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
    
    # Fetch equipment for the project
    cursor.execute('''
        SELECT equipment_type, last_maintenance_date, maintenance_schedule_days, status
        FROM equipment
        WHERE project_id = ?
    ''', (project_id,))
    equipment = cursor.fetchall()
    equipment_list = []
    for equip in equipment:
        last_maintenance = equip[1]
        schedule_days = equip[2]
        next_maintenance = 'Not scheduled'
        if last_maintenance and schedule_days:
            last_date = datetime.strptime(last_maintenance, '%Y-%m-%d')
            next_date = last_date + timedelta(days=schedule_days)
            next_maintenance = next_date.strftime('%Y-%m-%d')
        equipment_list.append({
            'equipment_type': equip[0],
            'last_maintenance_date': last_maintenance,
            'next_maintenance_date': next_maintenance,
            'status': equip[3]
        })
    
    # Fetch weather data based on project zip code
    weather_data = []
    try:
        with open('weather_api_key.txt', 'r') as f:
            api_key = f.read().strip()
            if not api_key:
                raise ValueError("API key is empty in weather_api_key.txt")
        
        # Get latitude and longitude from zip code using Geocoding API
        zip_code = project[6]  # zip_code from projects table
        if not zip_code:
            raise ValueError(f"No zip code found for project ID {project_id}")
        
        geo_params = {
            'zip': f"{zip_code},US",
            'appid': api_key
        }
        geo_response = requests.get("https://api.openweathermap.org/geo/1.0/zip", params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if 'lat' not in geo_data or 'lon' not in geo_data:
            raise ValueError(f"Geocoding API response missing lat/lon: {geo_data}")
        lat = geo_data.get('lat')
        lon = geo_data.get('lon')
        print(f"Fetched coordinates for zip {zip_code}: lat={lat}, lon={lon}")
        
        # Fetch 5-day forecast
        weather_params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'imperial'  # Fahrenheit
        }
        response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=weather_params)
        response.raise_for_status()
        forecast = response.json()
        if 'list' not in forecast:
            raise ValueError(f"Forecast API response missing list: {forecast}")
        
        # Get the most recent 5 days of forecast data
        daily_forecasts = {}
        project_start_date = datetime.strptime(project[3], '%Y-%m-%d')
        for entry in forecast['list']:
            entry_date = datetime.fromtimestamp(entry['dt']).date()
            if entry_date not in daily_forecasts:
                daily_forecasts[entry_date] = {
                    'date': entry_date.strftime('%Y-%m-%d'),
                    'temp': entry['main']['temp'],
                    'condition': entry['weather'][0]['main']
                }
            if len(daily_forecasts) >= 5:
                break
        
        weather_data = list(daily_forecasts.values())
        print(f"Fetched weather for zip {zip_code}: {len(weather_data)} days")
        
        # Check if forecast range covers project start date
        earliest_forecast_date = min(datetime.strptime(day['date'], '%Y-%m-%d').date() for day in weather_data)
        latest_forecast_date = max(datetime.strptime(day['date'], '%Y-%m-%d').date() for day in weather_data)
        if project_start_date.date() > latest_forecast_date:
            print(f"Weather forecast range {earliest_forecast_date} to {latest_forecast_date} does not cover project start date {project_start_date.date()}; showing most recent 5 days.")
            flash(f"Weather forecast is for {earliest_forecast_date} to {latest_forecast_date}, as the project start date ({project_start_date.date()}) is beyond the forecast range.", 'info')
    except FileNotFoundError:
        print("Failed to fetch weather data: weather_api_key.txt not found")
        flash('Unable to fetch weather data: API key file missing.', 'warning')
    except ValueError as ve:
        print(f"Failed to fetch weather data: {str(ve)}")
        flash('Unable to fetch weather data: Invalid project zip code or API response.', 'warning')
    except requests.exceptions.RequestException as re:
        print(f"Failed to fetch weather data: {str(re)}")
        flash('Unable to fetch weather data: API request failed.', 'warning')
    except Exception as e:
        print(f"Failed to fetch weather data: {str(e)}")
        flash('Unable to fetch weather data.', 'warning')
    
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
    return render_template('project.html', project=project_dict, customer=customer_dict, finances=finances_list, tasks=tasks_list, photos=photos, weather_data=weather_data, equipment=equipment_list)

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
        scheduler_mode = request.form.get('scheduler_mode')  # Check Scheduler Mode toggle

        # Validate dates if provided
        if start_date and due_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(due_date, '%Y-%m-%d')
            if end < start:
                flash('Due date cannot be earlier than start date.', 'danger')
                conn.close()
                return render_template('add_task.html', users=users, project_id=project_id)

        try:
            cursor.execute('''
                INSERT INTO tasks (project_id, description, assigned_to, status, start_date, end_date, duration_days, hours_spent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (project_id, title, assignee, status, start_date, due_date, duration_days, hours_spent))
            conn.commit()

            # Send email notification to assignee if assigned and Scheduler Mode is off
            if scheduler_mode == 'on':
                print("Scheduler Mode is on: Scheduling privately, skipping email notification")
                flash('Task added successfully! (Scheduled privately, no email sent)', 'success')
            else:
                if assignee:
                    cursor.execute('SELECT username, email FROM users WHERE id = ?', (assignee,))
                    assignee_data = cursor.fetchone()
                    if assignee_data:
                        username, email = assignee_data
                        if email:
                            cursor.execute('SELECT name FROM projects WHERE id = ?', (project_id,))
                            project_name = cursor.fetchone()[0]
                            subject = f"New Task Assigned: {title}"
                            body = f"You have been assigned a new task in the LG Asphalt Project Management Platform.\n\n" \
                                   f"Project: {project_name}\n" \
                                   f"Task: {title}\n" \
                                   f"Status: {status}\n" \
                                   f"Start Date: {start_date or 'Not specified'}\n" \
                                   f"Due Date: {due_date or 'Not specified'}\n" \
                                   f"Duration: {duration_days or 'Not specified'} days\n" \
                                   f"Hours Spent: {hours_spent or '0'} hours\n\n" \
                                   f"Please log in to the platform to view details: http://127.0.0.1:5000/login"
                            print(f"Sending email to {email} for task {title}")
                            if send_email(email, subject, body):
                                flash('Task added successfully!', 'success')
                            else:
                                flash('Task added successfully, but failed to send email notification.', 'success')
                        else:
                            print(f"Assignee {username} (ID {assignee}) has no email address")
                            flash('Task added successfully, but assignee has no email for notification.', 'success')
                    else:
                        print(f"No user found for assignee ID {assignee}")
                        flash('Task added successfully, but assignee not found for email notification.', 'success')
                else:
                    print("No assignee selected for task")
                    flash('Task added successfully, but no assignee selected for email notification.', 'success')

            return redirect(url_for('project', project_id=project_id))
        except Exception as e:
            flash(f'Error adding task: {str(e)}', 'danger')
        finally:
            conn.close()
    conn.close()
    return render_template('add_task.html', users=users, project_id=project_id)

@app.route('/project/<int:project_id>/add_equipment', methods=['GET', 'POST'])
@login_required
def add_equipment(project_id):
    user_id = getattr(current_user, 'id', None)
    is_authenticated = current_user.is_authenticated
    is_customer = getattr(current_user, '_is_customer', False)
    role = getattr(current_user, 'role', 'unknown')
    print(f"Add equipment access: user_id={user_id}, is_authenticated={is_authenticated}, is_customer={is_customer}, role={role}")

    if not is_authenticated:
        print("User not authenticated, redirecting to login")
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        role = user_data[0]
        print(f"Database role check: user_id={user_id}, role={role}")
        if role != 'admin':
            print(f"User {user_id} is not admin, redirecting to pm_dashboard")
            flash('Access restricted to admins.', 'danger')
            return redirect(url_for('pm_dashboard'))
    else:
        print(f"No user found in database for user_id={user_id}, redirecting to login")
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))
    conn.close()

    if is_customer:
        print(f"User {user_id} is customer, redirecting to customer_portal")
        flash('Access restricted to admins.', 'danger')
        return redirect(url_for('customer_portal'))

    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if not project:
        conn.close()
        print(f"Project {project_id} not found, redirecting to pm_dashboard")
        flash('Project not found.', 'danger')
        return redirect(url_for('pm_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        equipment_type = request.form.get('equipment_type')
        status = request.form.get('status')
        last_maintenance_date = request.form.get('last_maintenance_date') or None
        maintenance_schedule_days = request.form.get('maintenance_schedule_days') or None
        try:
            cursor.execute('''
                INSERT INTO equipment (project_id, name, equipment_type, status, last_maintenance_date, maintenance_schedule_days)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_id, name, equipment_type, status, last_maintenance_date, maintenance_schedule_days))
            conn.commit()
            flash('Equipment added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding equipment: {str(e)}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('project', project_id=project_id))

    conn.close()
    return render_template('add_equipment.html', project_id=project_id)

@app.route('/project/<int:project_id>/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo(project_id):
    user_id = getattr(current_user, 'id', None)
    is_authenticated = current_user.is_authenticated
    is_customer = getattr(current_user, '_is_customer', False)
    role = getattr(current_user, 'role', 'unknown')
    print(f"Upload photo access: user_id={user_id}, is_authenticated={is_authenticated}, is_customer={is_customer}, role={role}")

    if not is_authenticated:
        print("User not authenticated, redirecting to login")
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        role = user_data[0]
        print(f"Database role check: user_id={user_id}, role={role}")
        if role != 'admin':
            print(f"User {user_id} is not admin, redirecting to pm_dashboard")
            flash('Access restricted to admins.', 'danger')
            return redirect(url_for('pm_dashboard'))
    else:
        print(f"No user found in database for user_id={user_id}, redirecting to login")
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))
    conn.close()

    if is_customer:
        print(f"User {user_id} is customer, redirecting to customer_portal")
        flash('Access restricted to admins.', 'danger')
        return redirect(url_for('customer_portal'))

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
                print(f"Photo inserted: project_id={project_id}, filename={unique_filename}")
                flash('Photo uploaded successfully!', 'success')
                return redirect(url_for('project', project_id=project_id))
            except Exception as e:
                print(f"Error inserting photo: {str(e)}")
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