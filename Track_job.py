from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import abort
import csv
import io
from flask import Response

# --------Login/Registor Imports------

from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, flash
import os

from supabase import create_client, Client

supabase: Client = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_ANON_KEY')
)

supabase_admin: Client = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
db = SQLAlchemy(app)


# ----------Model----------
class Job(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='Applied')
    date_applied = db.Column(db.String)
    notes = db.Column(db.String)
    url = db.Column(db.String)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    interview_date = db.Column(db.String)
    deadline = db.Column(db.String)
    salary = db.Column(db.String)
    status_changed_at = db.Column(db.String)
    user_id = db.Column(db.String, nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    profile_pic = db.Column(db.Text, nullable=True)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.String, primary_key=True) 
    username = db.Column(db.String(50), unique=True, nullable=True)
    profile_pic = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)

# ---------Migration---------
with app.app_context():
    db.create_all()
   # migrate interview date, deadline, salary, status change column for existing databases
    try:
       with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE applications ADD COLUMN deadline TEXT'))
            conn.commit()
    except:
        pass
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE applications ADD COLUMN salary TEXT'))
            conn.commit()
    except:
        pass
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE applications ADD COLUMN status_changed_at TEXT'))
            conn.commit()
    except:
        pass

    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE profiles ADD COLUMN email TEXT'))
            conn.commit()
    except:
        pass

@app.before_request
def load_supabase_session():
    if 'access_token' in session and 'refresh_token' in session:
        try:
            supabase.auth.set_session(session['access_token'], session['refresh_token'])
        except Exception:
            pass

# ----------Index----------
@app.route('/')
def index():
    if 'loggedin' not in session:
        return render_template('landing.html')
    
    edit_id = request.args.get('edit_id', type=int)

    # Filtering for a job the user searchs for in the data
    search_query = request.args.get('q', '').strip()

    # Sorting the Jobs
    sort = request.args.get('sort', 'newest') 
    

    query = Job.query.filter_by(archived=False, user_id=session['id'])

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            (Job.company.ilike(like_pattern)) | (Job.role.ilike(like_pattern))
        )

    if sort == 'oldest':
        jobs = query.order_by(Job.id.asc()).all()
    
    else: 
        jobs = query.order_by(Job.id.desc()).all()

    statuses = ['Applied', 'Interview', 'Offer', 'Rejected']
    jobs_by_status = {status: [j for j in jobs if j.status == status] for status in statuses}

    # Application Stats bar -> This show the total application applied
    # Response Rate and the Interview Rate
    total_applied = Job.query.count()
    total_interviews = Job.query.filter_by(status='Interview').count()
    total_offers = Job.query.filter_by(status='Offer').count()
    total_rejections = Job.query.filter_by(status='Rejected').count()
    total_responses = total_interviews + total_offers + total_rejections

    response_rate = (total_responses / total_applied * 100) if total_applied > 0 else 0
    interview_rate = (total_interviews / total_applied * 100) if total_applied > 0 else 0
    offer_rate = (total_offers / total_applied * 100) if total_applied > 0 else 0
    rejected_rate = (total_rejections / total_applied * 100) if total_applied > 0 else 0
    
    profile = Profile.query.get(session['id'])

    return render_template(
        'index.html',
        jobs_by_status=jobs_by_status,
        edit_id=edit_id,
        search_query=search_query,
        sort=sort,
        total_applied=total_applied,
        response_rate=response_rate,
        interview_rate=interview_rate,
        offer_rate=offer_rate,
        rejected_rate=rejected_rate,
        
    )


# ----------Add Job----------
@app.route('/add', methods=['POST'])
def add_job():
    company = request.form['company']
    role = request.form['role']
    status = request.form['status']
    notes = request.form['notes']
    url = request.form['url']
    today = datetime.today().strftime('%Y-%m-%d')
    interview_date = request.form.get('interview_date', '')
    deadline = request.form.get('deadline', '')
    salary = request.form.get('salary', '')

    if company and role:
        new_job = Job(
    company=company, role=role, status=status, date_applied=today,
    notes=notes, url=url, user_id=session['id'],
    interview_date=interview_date, deadline=deadline, salary=salary
)
        db.session.add(new_job)
        db.session.commit()

    return redirect(url_for('index'))


# ----------Edit Job----------
@app.route('/edit/<int:job_id>', methods=['POST'])
def edit_job(job_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    job = db.session.get(Job, job_id)
    if not job: abort(404)

    job.company = request.form['company']
    job.role = request.form['role']
    job.status = request.form['status']
    job.notes = request.form['notes']
    job.url = request.form['url']
    job.interview_date = request.form.get('interview_date', '')

    # This checks if the status of the job did change or no
    if job.status != request.form['status']:
        job.status_changed_at = datetime.today().strftime('%Y-%m-%d')
    job.deadline = request.form.get('deadline', '')
    job.salary = request.form.get('salary', '')

    db.session.commit()
    return redirect(url_for('index'))


# ----------Update Status (drag & drop)----------
@app.route('/update-status/<int:job_id>', methods=['POST'])
def update_status(job_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    job = db.session.get(Job, job_id)
    if not job: return '', 404

    job.status = request.form['status']
    job.status_changed_at = datetime.today().strftime('%Y-%m-%d')
    db.session.commit()
    return '', 204


# ----------Delete Job----------
@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    job = db.session.get(Job, job_id)
    if not job: abort(404)

    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('index'))

# ----------Archived and Unarchived Jobs----------
@app.route('/archive/<int:job_id>', methods=['POST'])
def archive_job(job_id):
    job = db.session.get(Job, job_id)
    if not job: abort(404)
    job.archived = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/unarchive/<int:job_id>', methods=['POST'])
def unarchive_job(job_id):
    job = db.session.get(Job, job_id)
    if not job: abort(404)
    job.archived = False
    db.session.commit()
    return redirect(url_for('archived'))

@app.route('/archived')
def archived():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    jobs = Job.query.filter_by(archived=True).order_by(Job.id.desc()).all()
    profile = Profile.query.get(session['id'])
    return render_template('archived.html', jobs=jobs, profile=profile)

# ----------Job deadline----------
@app.template_filter('days_since')
def days_since(date_str):
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
    return (datetime.today() - d).days

@app.template_filter('days_until')
def days_until(date_str):
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
    return (d - datetime.today()).days

# ----------Login/Logout/Register----------
def validate_password(password):
    if len(password) < 8:
        return 'Password must be at least 8 characters.'
    if not any(c.isupper() for c in password):
        return 'Password must contain at least one uppercase letter.'
    if not any(c.islower() for c in password):
        return 'Password must contain at least one lowercase letter.'
    if not any(c.isdigit() for c in password):
        return 'Password must contain at least one number.'
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return 'Password must contain at least one special character.'
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        password = request.form['password']

        if '@' in identifier:
            email = identifier
        else:
            match = Profile.query.filter_by(username=identifier).first()
            if not match or not match.email:
                flash('Incorrect username or password.', 'error')
                return render_template('login.html')
            email = match.email

        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['loggedin'] = True
            session['id'] = result.user.id
            session['email'] = result.user.email
            session['access_token'] = result.session.access_token
            session['refresh_token'] = result.session.refresh_token
            return redirect(url_for('index'))
        except Exception as e:
            flash('Incorrect username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form['password']
        username = request.form.get('username', '').strip()

        error = validate_password(password)
        if error:
            flash(error, 'error')
            return render_template('register.html')

        try:
            result = supabase.auth.sign_up({"email": email, "password": password})
        except Exception as e:
            flash(str(e), 'error')
            return render_template('register.html')

        if result.user:
            profile = Profile(id=result.user.id, username=username, email=email)
            db.session.add(profile)
            db.session.commit()

        flash('Account created! Check your email to confirm, then log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    supabase.auth.sign_out()
    session.clear()
    return redirect(url_for('login'))

@app.route('/check-username')
def check_username():
    username = request.args.get('username', '').strip()
    if not username:
        return {'available': False}
    return {'available': not bool(Profile.query.filter_by(username=username).first())}

# ----------Google Auth----------
@app.route('/auth/google')
def auth_google():
    result = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": request.url_root.rstrip('/') + '/auth/callback'}
    })
    return redirect(result.url)

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    if not code:
        flash('Google sign-in failed.', 'error')
        return redirect(url_for('login'))
    try:
        result = supabase.auth.exchange_code_for_session({"auth_code": code})
        session['loggedin'] = True
        session['id'] = result.user.id
        session['email'] = result.user.email
        session['access_token'] = result.session.access_token
        session['refresh_token'] = result.session.refresh_token
        if not Profile.query.get(result.user.id):
            db.session.add(Profile(id=result.user.id, username=result.user.email.split('@')[0]))
            db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('login'))

# ----------Profile----------
@app.route('/profile')
def profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    profile_obj = Profile.query.get(session['id'])
    return render_template('profile.html', email=session.get('email'), profile=profile_obj)

@app.route('/profile/update-email', methods=['POST'])
def update_email():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    new_email = request.form.get('email', '').strip()
    try:
        supabase.auth.update_user({"email": new_email})
        session['email'] = new_email
        profile_obj = Profile.query.get(session['id'])
        if profile_obj:
            profile_obj.email = new_email
            db.session.commit()
        flash('Confirmation email sent to your new address. Check your inbox to finish the change.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('profile'))

@app.route('/profile/update-password', methods=['POST'])
def update_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    new_password = request.form.get('new_password', '')
    error = validate_password(new_password)
    if error:
        flash(error, 'error')
        return redirect(url_for('profile'))
    try:
        supabase.auth.update_user({"password": new_password})
        flash('Password updated.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('profile'))

@app.route('/profile/update-photo', methods=['POST'])
def update_photo():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    file = request.files.get('photo')
    if file and file.filename:
        import base64
        encoded = base64.b64encode(file.read()).decode('utf-8')
        data_url = f"data:{file.mimetype};base64,{encoded}"
        profile_obj = Profile.query.get(session['id'])
        if profile_obj:
            profile_obj.profile_pic = data_url
            db.session.commit()
        flash('Profile picture updated.', 'success')
    return redirect(url_for('profile'))

# ----------Delete Account----------
@app.route('/profile/delete-account', methods=['POST'])
def delete_account():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    user_id = session['id']
    try:
        Job.query.filter_by(user_id=user_id).delete()
        profile_obj = Profile.query.get(user_id)
        if profile_obj:
            db.session.delete(profile_obj)
        db.session.commit()
        supabase_admin.auth.admin.delete_user(user_id)
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('profile'))
    session.clear()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('login'))

# ----------Export Data----------
@app.route('/export/csv')
def export_csv():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    jobs = Job.query.filter_by(user_id=session['id']).order_by(Job.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Company', 'Role', 'Status', 'Date Applied', 'Interview Date',
        'Deadline', 'Salary', 'URL', 'Notes', 'Archived'
    ])
    for job in jobs:
        writer.writerow([
            job.company, job.role, job.status, job.date_applied,
            job.interview_date or '', job.deadline or '', job.salary or '',
            job.url or '', job.notes or '', 'Yes' if job.archived else 'No'
        ])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=ledger_export.csv'
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=8080)
