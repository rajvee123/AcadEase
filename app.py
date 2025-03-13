# app.py
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
import os
import pandas as pd
import sqlite3
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)

# Configure upload settings for results
UPLOAD_FOLDER = os.path.join('static', 'results')
ALLOWED_EXTENSIONS = {'pdf', 'csv'}

# Configure upload settings for events
EVENT_UPLOAD_FOLDER = os.path.join('static', 'uploads_event')
EVENT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EVENT_UPLOAD_FOLDER'] = EVENT_UPLOAD_FOLDER

# Ensure the upload folders exist
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

ensure_dir(app.config['UPLOAD_FOLDER'])
ensure_dir(app.config['EVENT_UPLOAD_FOLDER'])

# Check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_event_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EVENT_ALLOWED_EXTENSIONS

app.config['SECRET_KEY'] = 'your_secret_key'  # Change this in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize events database
def init_events_db():
    if os.path.exists('events.db'):
        os.remove('events.db')
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image_path TEXT,
        event_date DATE NOT NULL,
        event_time TIME NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(20))  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Decorator for verifying JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        
        if not token:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
            
            if not current_user:
                flash('User not found', 'danger')
                return redirect(url_for('login'))
                
        except jwt.ExpiredSignatureError:
            flash('Session expired. Please login again', 'warning')
            return redirect(url_for('login'))
        except:
            flash('Session invalid. Please login again', 'warning')
            return redirect(url_for('login'))
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Role-based access control decorators
def teacher_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'teacher':
            flash('Access denied: Teacher privileges required', 'danger')
            return redirect(url_for('index'))
        return f(current_user, *args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied: Student privileges required', 'danger')
            return redirect(url_for('index'))
        return f(current_user, *args, **kwargs)
    return decorated

# Main routes with templates
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('User not found', 'danger')
            return render_template('login.html')
        
        if check_password_hash(user.password, password):
            # Generate JWT token
            token = jwt.encode({
                'public_id': user.public_id,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            # Store in session
            session['token'] = token
            session['user_role'] = user.role
            session['user_name'] = user.name
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid password', 'danger')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        
        if not name or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if role not in ['student', 'teacher']:
            flash('Invalid role selected', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    return render_template('dashboard.html', user=current_user)

@app.route('/profile')
@token_required
def profile(current_user):
    return render_template('profile.html', user=current_user)

# Student-specific routes
@app.route('/view-materials')
@token_required
def view_materials(current_user):
    # In a real app, you would fetch materials from the database
    materials = [
        {'id': 1, 'title': 'Introduction to Python', 'subject': 'Programming'},
        {'id': 2, 'title': 'Web Development Basics', 'subject': 'Web Dev'},
        {'id': 3, 'title': 'Data Structures', 'subject': 'Computer Science'}
    ]
    return render_template('view_materials.html', materials=materials, user=current_user)

# Teacher-specific routes
@app.route('/upload-materials', methods=['GET', 'POST'])
@token_required
@teacher_required
def upload_materials(current_user):
    if request.method == 'POST':
        # In a real app, you would save files and metadata to database
        title = request.form.get('title')
        subject = request.form.get('subject')
        # file = request.files['material_file']
        
        flash(f'Material "{title}" uploaded successfully', 'success')
        return redirect(url_for('upload_materials'))
    
    return render_template('upload_materials.html', user=current_user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/upload_download')
@token_required
def upload_download(current_user):
    return render_template('upload_download.html', user=current_user)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Result system 
@app.route('/manage-results')
def manage_results():
    # Get years from directory structure
    years = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        years = [name for name in os.listdir(app.config['UPLOAD_FOLDER']) 
                if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], name))]
    
    return render_template('result/manage_results.html', years=years)

@app.route('/my-results')
def my_results():
    # Get years from directory structure
    years = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        years = [name for name in os.listdir(app.config['UPLOAD_FOLDER']) 
                if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], name))]
    
    return render_template('result/my_results.html', years=years)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    year = request.form.get('year')
    semester = request.form.get('semester')
    course = request.form.get('course')
    
    if not year:
        flash('Year is required')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Create year directory if it doesn't exist
        year_dir = os.path.join(app.config['UPLOAD_FOLDER'], year)
        ensure_dir(year_dir)
        
        # Generate a filename with semester and course if provided
        base_filename = secure_filename(file.filename)
        filename_parts = []
        
        if semester:
            filename_parts.append(f"Semester-{semester}")
        if course:
            filename_parts.append(f"Course-{course}")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename_parts.append(timestamp)
        
        if filename_parts:
            filename = f"{'_'.join(filename_parts)}_{base_filename}"
        else:
            filename = base_filename
        
        file_path = os.path.join(year_dir, filename)
        file.save(file_path)
        
        flash('File successfully uploaded')
        return redirect(url_for('manage_results'))
    
    flash('Invalid file type. Only PDF and CSV files are allowed.')
    return redirect(url_for('manage_results'))

@app.route('/browse/<year>')
def browse_results(year):
    year_dir = os.path.join(app.config['UPLOAD_FOLDER'], year)
    
    if not os.path.exists(year_dir):
        flash(f'No results found for year {year}')
        return redirect(url_for('student_dashboard'))
    
    files = os.listdir(year_dir)
    results = []
    
    for file in files:
        # Parse filename to extract metadata
        file_info = {
            'filename': file,
            'path': f"{year}/{file}",
            'semester': None,
            'course': None,
            'type': file.rsplit('.', 1)[1].lower()
        }
        
        # Extract semester and course from filename if present
        parts = file.split('_')
        for part in parts:
            if part.startswith('Semester-'):
                file_info['semester'] = part.replace('Semester-', '')
            elif part.startswith('Course-'):
                file_info['course'] = part.replace('Course-', '')
        
        results.append(file_info)
    
    # Get unique semesters and courses for filters
    semesters = sorted(list(set(file['semester'] for file in results if file['semester'])))
    courses = sorted(list(set(file['course'] for file in results if file['course'])))
    
    return render_template('result/browse.html', results=results, year=year, semesters=semesters, courses=courses)

@app.route('/filter_results', methods=['POST'])
def filter_results():
    year = request.form.get('year')
    semester = request.form.get('semester')
    course = request.form.get('course')
    
    if not year:
        flash('Year is required')
        return redirect(url_for('student_dashboard'))
    
    # Build the redirect URL with query parameters
    redirect_url = url_for('browse_results', year=year)
    query_params = []
    
    if semester and semester != 'all':
        query_params.append(f'semester={semester}')
    if course and course != 'all':
        query_params.append(f'course={course}')
    
    if query_params:
        redirect_url += '?' + '&'.join(query_params)
    
    return redirect(redirect_url)

@app.route('/download/<path:filepath>')
def download_file(filepath):
    directory, filename = os.path.split(filepath)
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], directory), filename, as_attachment=True)

@app.route('/preview/<path:filepath>')
def preview_file(filepath):
    directory, filename = os.path.split(filepath)
    file_type = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'pdf':
        file_url = url_for('static', filename=f'results/{filepath}')
        return render_template('result/preview_pdf.html', file_url=file_url, filename=filename)
    elif file_type == 'csv':
        try:
            # Read the CSV file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], directory, filename)
            df = pd.read_csv(file_path)
            return render_template('result/preview_csv.html', tables=[df.to_html(classes='data')], titles=df.columns.values, filename=filename)
        except Exception as e:
            flash(f'Error previewing CSV: {str(e)}')
            return redirect(url_for('browse_results', year=directory))
    
    flash('Preview not available for this file type')
    return redirect(url_for('browse_results', year=directory))

# Events System
@app.route('/events')
def events_home():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY event_date ASC')
    events = cursor.fetchall()
    conn.close()
    return render_template('Events/Event_index.html', events=events)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    event = cursor.fetchone()
    conn.close()
    if event:
        return render_template('Events/event_detail.html', event=event)
    flash('Event not found!', 'danger')
    return redirect(url_for('Events/index.html'))

@app.route('/upload_event', methods=['GET', 'POST'])
@token_required
@teacher_required
def upload_event(current_user):
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        
        # Form validation
        if not title or not description or not event_date or not event_time:
            flash('All fields except image are required!', 'danger')
            return redirect(url_for('upload_event'))
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_event_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to prevent filename conflicts
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['EVENT_UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_path = os.path.join('uploads_event', filename)
        
        # Database connection moved outside the image check
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO events (title, description, image_path, event_date, event_time) VALUES (?, ?, ?, ?, ?)',
            (title, description, image_path, event_date, event_time)
        )
        conn.commit()
        conn.close()
        
        flash('Event uploaded successfully!', 'success')
        return redirect(url_for('events_home'))  # Not 'Events/index.html'
    
    return render_template('Events/upload.html', user=current_user)

@app.route('/manage_events')
@token_required
@teacher_required
def manage_events(current_user):
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY event_date DESC')
    events = cursor.fetchall()
    conn.close()
    return render_template('Events/manage.html', events=events, user=current_user)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@token_required
@teacher_required
def delete_event(current_user, event_id):
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    
    # Get the image path before deleting
    cursor.execute('SELECT image_path FROM events WHERE id = ?', (event_id,))
    event = cursor.fetchone()
    
    if event and event[0]:
        # Delete the image file if it exists
        try:
            image_path = os.path.join('static', event[0])
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            flash(f'Error removing image: {str(e)}', 'warning')
    
    # Delete the event from database
    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('manage_events'))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@token_required
@teacher_required
def edit_event(current_user, event_id):
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        
        # Form validation
        if not title or not description or not event_date or not event_time:
            flash('All fields except image are required!', 'danger')
            return redirect(url_for('edit_event', event_id=event_id))
        
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        
        # Check if a new image was uploaded
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if allowed_event_file(file.filename):
                # Get the old image path
                cursor.execute('SELECT image_path FROM events WHERE id = ?', (event_id,))
                old_image_path = cursor.fetchone()[0]
                
                # Delete the old image if it exists
                if old_image_path:
                    try:
                        full_path = os.path.join('static', old_image_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    except Exception as e:
                        flash(f'Error removing old image: {str(e)}', 'warning')
                
                # Save the new image
                filename = secure_filename(file.filename)
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['EVENT_UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_path = os.path.join('uploads_event', filename)
                
                # Update with new image
                cursor.execute(
                    'UPDATE events SET title = ?, description = ?, image_path = ?, event_date = ?, event_time = ? WHERE id = ?',
                    (title, description, image_path, event_date, event_time, event_id)
                )
            else:
                flash('Invalid image format!', 'danger')
                return redirect(url_for('edit_event', event_id=event_id))
        else:
            # Update without changing the image
            cursor.execute(
                'UPDATE events SET title = ?, description = ?, event_date = ?, event_time = ? WHERE id = ?',
                (title, description, event_date, event_time, event_id)
            )
        
        conn.commit()
        conn.close()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('manage_events'))
    
    # GET request - show the edit form
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    event = cursor.fetchone()
    conn.close()
    
    if not event:
        flash('Event not found!', 'danger')
        return redirect(url_for('manage_events'))
    
    return render_template('Events/edit.html', event=event, user=current_user)

# Initialize the databases
with app.app_context():
    db.create_all()
    init_events_db()

if __name__ == '__main__':
    app.run(debug=True)