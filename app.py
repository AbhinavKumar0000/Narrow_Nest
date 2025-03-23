from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ats_processor import ATSProcessor
from email_service import send_email
import os


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruitment.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['SECRET_KEY'] = 'your-secret-key'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'recruiter_login'

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(120), nullable=False)
        role = db.Column(db.String(20), default='recruiter')

    class Job(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(120), nullable=False)
        description = db.Column(db.Text, nullable=False)
        email = db.Column(db.String(120), nullable=False)

    class Applicant(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
        email = db.Column(db.String(120), nullable=False)
        resume_path = db.Column(db.String(200), nullable=False)
        ats_score = db.Column(db.Float)
        chatbot_score = db.Column(db.Float)
        video_path = db.Column(db.String(200))

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def landing():
        return render_template('landing.html', user=current_user)

    @app.route('/recruiter-login', methods=['GET', 'POST'])
    def recruiter_login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password) and user.role == 'recruiter':
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        return render_template('recruiter_login.html')

    @app.route('/recruiter-signup', methods=['GET', 'POST'])
    def recruiter_signup():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose another.', 'error')
            else:
                hashed_password = generate_password_hash(password)
                user = User(username=username, password=hashed_password, role='recruiter')
                db.session.add(user)
                db.session.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('recruiter_login'))
        return render_template('recruiter_signup.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('landing'))

    @app.route('/recruiter-home')
    @login_required
    def index():
        jobs = Job.query.all()
        data = []
        for job in jobs:
            applicants = Applicant.query.filter_by(job_id=job.id).all()
            applicant_info = [
                {
                    'id': applicant.id,
                    'email': applicant.email,
                    'ats_score': applicant.ats_score,
                    'chatbot_score': applicant.chatbot_score
                }
                for applicant in sorted(applicants, key=lambda x: (x.ats_score if x.ats_score is not None else 0), reverse=True)
            ]
            data.append({'job': job, 'applicant_count': len(applicants), 'applicants': applicant_info})
        return render_template('home.html', jobs=data)

    @app.route('/post_job', methods=['POST'])
    @login_required
    def post_job():
        title = request.form['title']
        description = request.form['description']
        email = request.form['email']
        job = Job(title=title, description=description, email=email)
        db.session.add(job)
        db.session.commit()
        return jsonify({
            'message': 'Job created successfully',
            'link': url_for('apply', job_id=job.id, _external=True)
        })

    @app.route('/job_list')
    def job_list():
        jobs = Job.query.all()
        return render_template('job_list.html', jobs=jobs)

    @app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
    def apply(job_id):
        job = Job.query.get_or_404(job_id)
        if request.method == 'POST':
            email = request.form['email']
            resume = request.files['resume']
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
            resume.save(resume_path)

            ats_processor = ATSProcessor()
            ats_score = ats_processor.calculate_score(resume_path)

            applicant = Applicant(job_id=job_id, email=email, resume_path=resume_path, ats_score=ats_score)
            db.session.add(applicant)
            db.session.commit()

            chatbot_link = url_for('chatbot', applicant_id=applicant.id, _external=True)
            video_link = url_for('upload_video', applicant_id=applicant.id, _external=True)
            quiz_link = url_for('quiz', job_id=job_id, _external=True)
            send_email(
                email,
                "Next Steps: Chatbot Interview & Video Submission",
                f"Congratulations! You've applied for {job.title}.\n"
                f"Complete your chatbot interview here: {chatbot_link}\n"
                f"Submit your video here: {video_link}\n"
                f"Take the quiz here: {quiz_link}"
            )

            return jsonify({'message': 'Application submitted successfully!'}), 200
        return render_template('apply.html', job=job)

    @app.route('/get_applicants/<int:job_id>')
    @login_required
    def get_applicants(job_id):
        job = Job.query.get_or_404(job_id)
        applicants = Applicant.query.filter_by(job_id=job_id).all()
        applicant_data = [
            {'email': a.email, 'ats_score': a.ats_score, 'chatbot_score': a.chatbot_score}
            for a in sorted(applicants, key=lambda x: (x.ats_score if x.ats_score is not None else 0), reverse=True)
        ]
        return jsonify({'applicant_count': len(applicants), 'applicants': applicant_data})

    @app.route('/chatbot/<int:applicant_id>')
    def chatbot(applicant_id):
        applicant = Applicant.query.get_or_404(applicant_id)
        return render_template('chatbot.html', applicant=applicant)

    @app.route('/upload_video/<int:applicant_id>', methods=['GET', 'POST'])
    def upload_video(applicant_id):
        applicant = Applicant.query.get_or_404(applicant_id)
        if request.method == 'POST':
            video = request.files['video']
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
            video.save(video_path)
            applicant.video_path = video_path
            db.session.commit()
            return redirect(url_for('results', applicant_id=applicant_id))
        return render_template('upload_video.html', applicant=applicant)

    @app.route('/quiz/<int:job_id>')
    def quiz(job_id):
        job = Job.query.get_or_404(job_id)
        return render_template('quiz.html', job=job)

    @app.route('/results/<int:applicant_id>')
    def results(applicant_id):
        applicant = Applicant.query.get_or_404(applicant_id)
        return render_template('results.html', applicant=applicant)

    return app