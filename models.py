from app import db

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