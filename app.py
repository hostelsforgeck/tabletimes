import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Load the timetable data
with open('timetable.json', 'r') as file:
    timetable_data = json.load(file)

@app.route('/')
def index():
    # Get list of colleges, departments, and semesters for the form
    colleges = list(timetable_data.keys())
    departments = {}
    semesters = {}
    
    for college in colleges:
        departments[college] = list(timetable_data[college].keys())
        semesters[college] = {}
        for dept in departments[college]:
            semesters[college][dept] = list(timetable_data[college][dept].keys())
    
    return render_template('index.html', colleges=colleges, departments=departments, semesters=semesters)

@app.route('/timetable', methods=['POST'])
def show_timetable_form():
    college = request.form.get('college')
    department = request.form.get('department')
    semester = request.form.get('semester')
    
    # Redirect to the direct URL
    return redirect(url_for('show_timetable', college=college, department=department, semester=semester))

@app.route('/<college>/<department>/<semester>')
def show_timetable(college, department, semester):
    try:
        # Check if the keys exist in the data structure
        if college not in timetable_data:
            return render_template('error.html', message=f"College '{college}' not found")
        
        if department not in timetable_data[college]:
            return render_template('error.html', message=f"Department '{department}' not found in '{college}'")
        
        if semester not in timetable_data[college][department]:
            return render_template('error.html', message=f"Semester '{semester}' not found in '{college}/{department}'")
        
        # Get the timetable for the specified college, department, and semester
        timetable = timetable_data[college][department][semester]
        
        # Get current day and time
        now = datetime.now()
        current_day = now.strftime('%A')
        current_time = now.strftime('%H:%M:%S')
        
        # Find the current class if it exists
        current_class = None
        if current_day in timetable:
            for session in timetable[current_day]:
                if session['start'] <= current_time <= session['end']:
                    current_class = session
                    break
        
        # Debug information
        print(f"Loading timetable for: {college}/{department}/{semester}")
        
        return render_template(
            'timetable.html',
            college=college,
            department=department,
            semester=semester,
            timetable=timetable,
            current_day=current_day,
            current_time=current_time,
            current_class=current_class
        )
    except Exception as e:
        return render_template('error.html', message=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)