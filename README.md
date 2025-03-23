# Narrow_Nest
Narrow_Nest
Narrow Nest - Recruitment Simplified
Narrow Nest is a Flask-based web application designed to streamline the hiring process. It allows recruiters to post jobs, manage applicants, and evaluate candidates using ATS scores, chatbot interviews, and video analysis. Applicants can browse jobs, submit resumes, and participate in chatbot interviews.

Features
For Recruiters
Post Jobs: Create and publish job listings with titles, descriptions, and contact emails.
Manage Applicants: View and evaluate applicants with ATS scores, chatbot responses, and video analysis.
Share Job Links: Generate and share unique job application links.
For Applicants
Browse Jobs: View all available job listings.
Apply for Jobs: Submit resumes and participate in chatbot interviews.
Video Submission: Upload video responses for confidence analysis.
Technologies Used
Backend: Flask (Python)
Frontend: HTML, CSS, JavaScript
Database: SQLite (with Flask-SQLAlchemy)
Authentication: Flask-Login
File Uploads: Resume and video uploads with Flask
Email Notifications: Flask-Mail (or custom email service)
ATS Scoring: Custom ATS scoring logic
Video Analysis: Custom NLP-based confidence scoring
Installation
Prerequisites
Python 3.8 or higher
Pip (Python package manager)
Steps
Clone the repository:
git clone https://github.com/your-username/narrow-nest.git
cd narrow-nest
Create a virtual environment:

bash Copy python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate Install dependencies:

bash Copy pip install -r requirements.txt Set up environment variables:

Create a .env file in the root directory.

Add the following variables:

env Copy DATABASE_URL=sqlite:///recruitment.db SECRET_KEY=your-secret-key Initialize the database:

bash Copy flask shell

db.create_all() exit() Run the application:

bash Copy python run.py Open your browser and navigate to:

Copy http://127.0.0.1:5000/ Project Structure Copy narrow-nest/ ├── app.py # Main Flask application ├── run.py # Entry point to run the app ├── requirements.txt # List of dependencies ├── .env # Environment variables ├── templates/ # HTML templates │ ├── landing.html # Landing page │ ├── recruiter_login.html # Recruiter login page │ ├── recruiter_signup.html # Recruiter signup page │ ├── home.html # Recruiter dashboard │ ├── apply.html # Job application page │ ├── chatbot.html # Chatbot interview page │ ├── upload_video.html # Video upload page │ └── results.html # Application results page ├── static/ # Static files (CSS, JS, images) ├── uploads/ # Uploaded resumes and videos └── README.md # Project documentation Usage Recruiter Flow Sign Up: Create a recruiter account.

Log In: Access the recruiter dashboard.

Post Jobs: Add new job listings.

Manage Applicants: View and evaluate applicants.

Applicant Flow Browse Jobs: View available job listings.

Apply for Jobs: Submit resumes and complete chatbot interviews.

Upload Video: Submit video responses for confidence analysis.

Acknowledgments Flask Documentation: https://flask.palletsprojects.com/

Flask-Login Documentation: https://flask-login.readthedocs.io/

SQLAlchemy Documentation: https://www.sqlalchemy.org/
