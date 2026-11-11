from flask import Flask, render_template, request, session, Response, send_from_directory
import random
import csv
import io
import os

app = Flask(__name__)
app.secret_key = "raj_gautam_personal_secret"

# In-memory storage (data resets when server stops)
students_data = {}
ADMIN_PASSWORD = "raj123"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/exam-form')
def exam_form():
    return render_template('exam-form.html')


@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    name = request.form.get('name', '').strip()
    roll = request.form.get('roll', '').strip()
    course = request.form.get('course', '').strip()
    dob = request.form.get('dob', '').strip()

    subjects = ["HTML", "CSS", "JavaScript", "Python", "Web Design"]
    marks_data = []
    total_obtained = 0
    for sub in subjects:
        marks = random.randint(60, 98)
        total_obtained += marks
        marks_data.append({"subject": sub, "marks": marks})

    total_marks = len(subjects) * 100
    percentage = round((total_obtained / total_marks) * 100, 2)
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 60:
        grade = "B"
    else:
        grade = "C"

    record = {
        "name": name.upper(),
        "roll": roll,
        "course": course,
        "dob": dob,
        "marks_data": marks_data,
        "total_obtained": total_obtained,
        "total_marks": total_marks,
        "percentage": percentage,
        "grade": grade,
    }
    students_data[roll] = record
    session['current_roll'] = roll
    return render_template('marksheet.html', **record)


@app.route('/view-marksheet/<roll>')
def view_marksheet(roll):
    data = students_data.get(roll)
    if not data:
        return "Marksheet nahi mili! Pehle exam form bharein.", 404
    return render_template('marksheet.html', **data)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
        else:
            return render_template('admin.html', logged_in=False, error="Galat Password!")
    if session.get('admin_logged_in'):
        return render_template('admin.html', logged_in=True, students=students_data)
    return render_template('admin.html', logged_in=False)


@app.route('/logout-admin')
def logout_admin():
    session.pop('admin_logged_in', None)
    return render_template('admin.html', logged_in=False)


@app.route('/export-csv')
def export_csv():
    if not session.get('admin_logged_in'):
        return "Access Denied! Pehle Admin login karein.", 403
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Roll No', 'Name', 'Course', 'DOB', 'Total Marks', 'Obtained Marks', 'Percentage', 'Grade'])
    for roll, data in students_data.items():
        writer.writerow([roll, data['name'], data['course'], data['dob'], data['total_marks'], data['total_obtained'], data['percentage'], data['grade']])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=students_report.csv'})


# Serve existing static syllabus pages and assets
@app.route('/html/<path:filename>')
def html_pages(filename):
    return send_from_directory('html', filename)


@app.route('/css/<path:filename>')
def css_pages(filename):
    return send_from_directory('css', filename)


@app.route('/js/<path:filename>')
def js_pages(filename):
    return send_from_directory('js', filename)


@app.route('/style.css')
def root_style():
    return send_from_directory('.', 'style.css')


@app.route('/logo.png')
def root_logo():
    return send_from_directory('.', 'logo.png')


@app.route('/develeper%20image%20.jpg')
@app.route('/develeper image .jpg')
def root_dev_image():
    return send_from_directory('.', 'develeper image .jpg')


if __name__ == '__main__':
    app.run(debug=True)
