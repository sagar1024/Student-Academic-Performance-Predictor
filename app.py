from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import numpy as np
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from flask import session
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.secret_key = 'asdfs34kak5'

db = SQLAlchemy(app)

class LoginDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Add the login details of the two users to the database
# @app.before_request
# def create_login_details():
#     # Check if the login details already exist
#     existing_login_details = LoginDetail.query.all()
#     if not existing_login_details:
#         # Create login details for the two users
#         user1 = LoginDetail(register_number='2347222', password='41705680')
#         user2 = LoginDetail(register_number='2347250', password='41705790')
#         db.session.add(user1)
#         db.session.add(user2)
#         db.session.commit()

# Define the login form
class LoginForm(FlaskForm):
    register_number = StringField('Register Number', validators=[DataRequired(), Length(min=1, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), unique=False, nullable=False)
    semester = db.Column(db.String(10), nullable=False)

    # Add relationship with Subject model
    subjects = db.relationship('Subject', back_populates='student')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cia_1 = db.Column(db.Integer, nullable=False)
    mid_sem = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    student_id = db.Column(db.String(10), db.ForeignKey('student.student_id'), nullable=False)

    # Add relationship with Student model
    student = db.relationship('Student', back_populates='subjects')
    
#Load the data
marks_data = pd.read_csv("marks_dataset.csv")

# Sample data for training the model
cia_1_scores = marks_data['Exam1']
mid_semester_scores = marks_data['Exam2']
end_result_percentages = marks_data['Next_exam']

# Train the model
X = np.column_stack((cia_1_scores, mid_semester_scores))
y = end_result_percentages
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for handling login
@app.route('/loginS', methods=['GET', 'POST'])
def logins():
    form = LoginForm()
    if form.validate_on_submit():
        # Check credentials
        login_detail = LoginDetail.query.filter_by(
            register_number=form.register_number.data
        ).first()
        if login_detail and login_detail.password == form.password.data:
            return redirect(url_for('studentform'))  # Successful login
        else:
            flash("Invalid registration number or password")  # Error message
    return render_template('loginS.html', form=form)

@app.route('/loginT')
def logint():
    return render_template('loginT.html')

@app.route('/oops')
def oops():
    return render_template('oops.html')

@app.route('/studentForm', methods=['GET', 'POST'])
def studentform():
    if request.method == 'POST':
        student_id = request.form['student_id']
        semester = request.form['subject_1_semester']

        # Create a new student
        new_student = Student(student_id=student_id, semester=semester)
        db.session.add(new_student)
        db.session.commit()

        # Retrieve subjects, CIA scores, and Midsem scores
        subjects = []
        cia_scores = []
        midsem_scores = []

        # Iterate through subject inputs dynamically
        for i in range(1, int(request.form['subject_count']) + 1):
            subject_name = request.form[f'subject_{i}_name']
            cia_score = request.form[f'subject_{i}_cia']
            midsem_score = request.form[f'subject_{i}_midsem']

            # **Corrected check using all()**
            if all([subject_name, cia_score, midsem_score]):  # Ensure all fields are filled
                subjects.append(subject_name)
                cia_scores.append(cia_score)
                midsem_scores.append(midsem_score)

                # Create a new subject
                new_subject = Subject(
                    name=subject_name,
                    cia_1=cia_score,
                    mid_sem=midsem_score,
                    semester=semester,
                    student_id=student_id
                )
                db.session.add(new_subject)

        db.session.commit()

        return redirect(url_for('predict', student_id=student_id, _external=True))

    return render_template('studentForm.html')

@app.route('/predict/<student_id>', methods=["GET", "POST"])
def predict(student_id):
    # Retrieve subjects, CIA scores, and Midsem scores from the database
    student = Student.query.filter_by(student_id=student_id).first()

    if student is not None:  # Check if the student exists
        subjects = [subject.name for subject in student.subjects]
        cia_scores = [subject.cia_1 for subject in student.subjects]
        midsem_scores = [subject.mid_sem for subject in student.subjects]

        # Convert scores to integers
        cia_scores = list(map(int, cia_scores))
        midsem_scores = list(map(int, midsem_scores))

        # Predict end result percentage for all subjects
        new_student_scores = np.array([cia_scores, midsem_scores]).T
        predicted_end_result_percentages = model.predict(new_student_scores).round(2)

        overall_predicted_score = np.mean(predicted_end_result_percentages)
        overall_predicted_score = round(min(overall_predicted_score, 100), 2)

        # Store data in a dictionary for each subject
        subject_data = []
        for i, subject in enumerate(subjects):
            subject_data.append({
                'x': ['CIA', 'Midsem', 'Predicted'],
                'y': [cia_scores[i], midsem_scores[i], predicted_end_result_percentages[i]],
                'name': subject,
                'mode': 'lines+markers',  # Line plot with markers
                'type': 'scatter'
            })

        # Define layout for the line chart
        line_layout = {
            'title': 'Predicted Scores Comparison',
            'xaxis': {'title': 'Exam Type'},
            'yaxis': {'title': 'Score (%)'},
            'legend': {'x': 1, 'y': 1, 'bgcolor': 'rgba(255, 255, 255, 0.5)'},
            'plot_bgcolor': '#f8f9fa',  # Plot background color
            'paper_bgcolor': '#f8f9fa',  # Paper background color
            'font': {'color': '#343a40'}  # Font color
        }

        # Generate HTML representation of the line chart
        graph_html_line = go.Figure(data=subject_data, layout=line_layout).to_html(full_html=False)

        # Render the prediction page with the line graph
        return render_template('prediction.html', subjects=subjects,
                               prediction=predicted_end_result_percentages.tolist(), student_id=student_id,
                               overall_predicted_score=overall_predicted_score,
                               graph_html_line=graph_html_line)

    # If the student is not found, redirect to the error page or handle as appropriate
    return redirect(url_for('oops'))

@app.route('/compare', methods=["POST"])
def compare():
    # Get actual end result percentage from the form
    actual_score = float(request.form['actual_score'])
    student_id = request.form['student_id']

    # Retrieve predicted end result percentage from the prediction model
    student = Student.query.filter_by(student_id=student_id).first()
    cia_scores = [subject.cia_1 for subject in student.subjects]
    midsem_scores = [subject.mid_sem for subject in student.subjects]
    cia_scores = list(map(int, cia_scores))
    midsem_scores = list(map(int, midsem_scores))
    new_student_scores = np.array([cia_scores, midsem_scores]).T
    predicted_end_result_percentages = model.predict(new_student_scores).round(2)
    overall_predicted_score = np.mean(predicted_end_result_percentages)

    # Calculate model accuracy
    model_accuracy = 100 - abs(actual_score - overall_predicted_score)
    return render_template('prediction.html', student_id=student_id, model_accuracy=round(model_accuracy, 2))

if __name__ == '__main__':
    app.run(debug=True)