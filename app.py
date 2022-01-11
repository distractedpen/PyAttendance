""" Attendance Taking App"""
from os import path
from datetime import date
from flask import (
    Flask, render_template, redirect, request, url_for
)

###
# Paths to each of the required files
###
BASEPATH = "../data/"
CANVAS_FILENAME = "canvas.txt"
STUDENTS_FILENAME = "students.txt"
ACCOUNTS_FILENAME = "accounts.txt"
ATTENDANCE_FILENAME = "attendance.csv"

canvas_path = path.join(BASEPATH, CANVAS_FILENAME)
students_path = path.join(BASEPATH, STUDENTS_FILENAME)
accounts_path = path.join(BASEPATH, ACCOUNTS_FILENAME)
attendance_path = path.join(BASEPATH, ATTENDANCE_FILENAME)


# Additions
# - Arrow Buttons to move to next/previous day
# - Eventually use numbers in place of student names
# - Warnings for students who miss more than 3 classes in a row

###
# Helper Functions
###

def get_accounts():
    """ Open the accounts.txt file and return a list of student names and accounts """
    with open(accounts_path, 'r', encoding='utf-8') as file_d:
        data = file_d.read().strip()
        accounts = data.split("\n")
        scrubbed_accounts = []
        for account in accounts:
            scrubbed_account = [account[0], account[1]] ## remove password
            scrubbed_accounts.append(scrubbed_account)
        return scrubbed_accounts

def get_students():
    """ Open the students.txt file ang return a list of student names. """
    with open(students_path, 'r', encoding='utf-8') as file_d:
        data = file_d.read().strip()
        students = data.split("\n")
    return students

def load_attendance_data():
    """ Get Attendance data from attendance.csv.
        If attendance.csv does not exist,
        create new attendance_data object using students.txt.
    """
    if not path.exists(attendance_path):
        students = get_students()
        attendance_dict = {student:[] for student in students}
        header = ["name"]
        return attendance_dict, header

    with open(attendance_path, 'r', encoding='utf-8') as file_d:
        data = file_d.read().strip("\n")
        student_att_data = data.split("\n")
        header = student_att_data.pop(0).split(",") # name, dates...
        attendance_dict = {}
        for str_data in student_att_data:
            str_data_list = str_data.split(",")
            name = str_data_list[0]
            str_presense = str_data_list[1:]
            presence = []
            for entry in str_presense:
                if entry == "True":
                    presence.append(True)
                else:
                    presence.append(False)
            attendance_dict[name] = presence
        return attendance_dict, header

def save_attendance_data(attendance_data, header):
    """ Save attendance data to attendance.csv """
    with open(attendance_path, 'w', encoding='utf-8') as file_d:
        file_d.write(",".join(header) + "\n")
        for name in attendance_data:
            rec_presence = [str(entry) for entry in attendance_data[name]]
            rec = ",".join([name] + rec_presence)
            file_d.write(rec + "\n")

def attendance_taken(given_date):
    """ Determine if attendance has be taken on date.
        Returns list of False if not.
        Returns list of True/False for Present/Absent
    """
    attendence_data, header = load_attendance_data()
    dates = header[1:]

    if date not in dates:
        return [False]*len(attendence_data)

    presense = []
    loc = dates.index(given_date)
    for name in attendence_data:
        presense.append(attendence_data[name][loc])
    return presense

def get_readable_date(given_date):
    """ Convert string date to readable format. """
    year, month, day = given_date.split("-")
    return f"{month}/{day}/{year}"

###
# App Creation
###

app = Flask(__name__)

###
#App Routes
###

@app.route('/')
def index():
    """ Get todays date and redirect to new attendance for today """
    today = date.today().isoformat()
    return redirect(url_for('attendance', date=today))

@app.route('/attendance/<date>', methods=("GET", "POST"))
def attendance(given_date):
    """ Displays Attendance Page for date.
        on HTML POST, attendance data is saved to attendance.csv
        on HTML GET, attendance data is loaded from attendance.csv
           if new date, display list of empty checkboxes.
    """
    students = get_students()

    readable_date = get_readable_date(given_date)

    if request.method == "POST":
        todays_attendance = request.form.getlist("present")
        all_attendance_dict, header = load_attendance_data()
        header.append(given_date)
        for name in all_attendance_dict:
            all_attendance_dict[name].append(False)
        for name in todays_attendance:
            all_attendance_dict[name][-1] = True
        save_attendance_data(all_attendance_dict, header)

    presense = attendance_taken(given_date)
    student_data = {students[i]:presense[i] for i in range(len(students))}
    return render_template("attendance.html", date=readable_date,
        student_data=student_data, table_size=5)


@app.route('/attendance/grid')
def grid():
    """ Show the number of days present/missed by student in a grid """
    all_attendance_dict, header = load_attendance_data()
    print(all_attendance_dict)
    return render_template("attendance-grid.html", dates=header,
        attendance_data=all_attendance_dict.items())


@app.route("/attendance/<wanted_account>")
def attendance_by_account(wanted_account):
    """ Get attendance data for student associate with wanted_account """
    accounts = get_accounts()
    all_attendance_dict, header = load_attendance_data()

    name = None
    for account in accounts:
        if account[1] == wanted_account:
            name = account[0]
            break

    if name is None:
        status_message = "No student associated with this account number."
        return render_template("error.html", status_message=status_message)
    return render_template("attendance-by-account.html", dates=header,
        attendence_data=all_attendance_dict[name])
