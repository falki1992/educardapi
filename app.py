from flask import Flask
from controller.admin_controller import setup_routes

app = Flask(__name__)

@app.route("/")
def welcome():
    return "Hello, Flask!"

# Set up the routes from admin_controller
setup_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
