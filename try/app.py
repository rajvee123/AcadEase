# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_materials.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_teacher = db.Column(db.Boolean, default=False)
    materials = db.relationship('Material', backref='uploader', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)
    materials = db.relationship('Material', backref='subject', lazy=True)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # Notes, PDF, PPT, Past Paper
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    semester = db.Column(db.String(20), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    subjects = Subject.query.all()
    recent_materials = Material.query.order_by(Material.upload_date.desc()).limit(5).all()
    return render_template('studyMaterial/index.html', subjects=subjects, recent_materials=recent_materials)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_teacher = 'is_teacher' in request.form
        
        # Check if user exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_teacher=is_teacher
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/materials')
def browse_materials():
    subject_id = request.args.get('subject', type=int)
    semester = request.args.get('semester')
    file_type = request.args.get('type')
    
    query = Material.query
    
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if semester:
        query = query.filter_by(semester=semester)
    if file_type:
        query = query.filter_by(file_type=file_type)
    
    materials = query.order_by(Material.upload_date.desc()).all()
    subjects = Subject.query.all()
    
    # Get unique semesters and file types for filtering
    semesters = db.session.query(Material.semester).distinct().all()
    file_types = db.session.query(Material.file_type).distinct().all()
    
    return render_template(
        'studyMaterial/materials.html', 
        materials=materials, 
        subjects=subjects, 
        semesters=semesters, 
        file_types=file_types,
        current_subject=subject_id,
        current_semester=semester,
        current_type=file_type
    )

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_material():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        subject_name = request.form.get('subject')
        semester = request.form.get('semester')
        file_type = request.form.get('file_type')
        file = request.files.get('file')
        
        if not title or not subject_name or not semester or not file_type or not file:
            flash('All fields are required')
            return redirect(url_for('upload_material'))
        
        # Check if subject exists, if not create it
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            # Generate a code from the name (first letter of each word, uppercase)
            code = ''.join([word[0].upper() for word in subject_name.split() if word])
            # If code exists already, add a number to make it unique
            base_code = code
            counter = 1
            while Subject.query.filter_by(code=code).first():
                code = f"{base_code}{counter}"
                counter += 1
                
            # Create new subject
            subject = Subject(name=subject_name, code=code)
            db.session.add(subject)
            db.session.commit()
            
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create new material
        new_material = Material(
            title=title,
            description=description,
            file_path=unique_filename,
            file_type=file_type,
            semester=semester,
            subject_id=subject.id,
            user_id=current_user.id
        )
        
        db.session.add(new_material)
        db.session.commit()
        
        flash('Material uploaded successfully!')
        return redirect(url_for('browse_materials'))
    
    return render_template('studyMaterial/upload.html')
@app.route('/download/<int:material_id>')
@login_required
def download_material(material_id):
    material = Material.query.get_or_404(material_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], material.file_path, as_attachment=True)

@app.route('/manage_subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if not current_user.is_teacher:
        flash('Only teachers can manage subjects')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        
        if Subject.query.filter_by(code=code).first():
            flash('Subject code already exists')
        else:
            new_subject = Subject(name=name, code=code)
            db.session.add(new_subject)
            db.session.commit()
            flash('Subject added successfully')
    
    subjects = Subject.query.all()
    return render_template('studyMaterial/manage_subjects.html', subjects=subjects)

@app.route('/delete_material/<int:material_id>', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    
    # Check if user is authorized to delete
    if material.user_id != current_user.id and not current_user.is_teacher:
        flash('You are not authorized to delete this material')
        return redirect(url_for('browse_materials'))
    
    # Delete file
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], material.file_path))
    except:
        pass  # File might not exist
    
    # Delete record
    db.session.delete(material)
    db.session.commit()
    
    flash('Material deleted successfully')
    return redirect(url_for('browse_materials'))

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=2000)