from app import app  # Import the Flask app instance from app.py

@app.route("/teacher/add")
def teacherCreate():
    return "Teacher created"
