from app import app


@app.route("/class/create")
def create():
    return "cleass created"