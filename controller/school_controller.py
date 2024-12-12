from app import app
from flask import request, jsonify,session
from flask_mail import Mail, Message
from model.school_model import school_model
import hashlib
from model.user_model import user_model


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'support@driveree.com'
app.config['MAIL_PASSWORD'] = 'dxskgtxwnvodkkog'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

obj=school_model()
userObj= user_model()


@app.route('/school/register', methods=['POST'])
def register_school():
    token=request.headers.get('Authorization')
    print(token)
    """Fetch and return dashboard data in JSON format using token."""
    try:
        # Extract the token from the request header

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        # Verify the token and get the user ID
        user = userObj.verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        uid = user['id']  # Extract user ID from the token verification
        data = request.json

    # Validate input
        required_fields = ['name', 'principal_name', 'school_uuid', 'password', 'email', 'mobile_number']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'All fields are required'}), 400

        school_name = data['name']
        principal_name = data['principal_name']
        school_id = data['school_uuid']
        password = data['password']
        email = data['email']
        mobile_number = data['mobile_number']
        password_hash = generate_md5(password)
        created_by=uid


        # Check if school_id or email already exists
        if obj.find_school_by_email_or_id(email, school_id):
            return jsonify({'error': 'School ID or Email already exists'}), 409

        # Hash the password
        hashed_password = obj.hash_password(password)

        # Register the school in the database
        registration_status = obj.register_school(
            school_name, principal_name, school_id, password_hash, email, mobile_number,created_by
        )

        if not registration_status['status']:
            return jsonify({'error': registration_status['message']}), 500

        # Send login details via email
        try:
            send_email(email, school_id, password)
            return jsonify({'message': 'School registered successfully'}), 201
        except Exception as e:
            return jsonify({'error': f'School registered, but failed to send email: {str(e)}'}), 200
    except Exception as err:
        return jsonify({"error": f"Error: {err}"}), 500

@app.route('/schools/all', methods=['GET'])
def get_all_schools():

    """Fetch all schools."""
    try:
        schools = obj.get_schools_by_status(None)  # Get all schools without filtering by status
        return jsonify({'status': 'ok','message':'Successfully get all schools', 'data': schools}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/schools/pending', methods=['GET'])
def get_pending_schools():
    """Fetch schools with status 0 (pending)."""
    try:
        schools = obj.get_schools_by_status("0")  # Get pending schools
        return jsonify({'status': 'success', 'message':'Successfully get pending schools','data': schools}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/schools/active', methods=['GET'])
def get_active_schools():
    """Fetch schools with status 1 (active)."""
    try:
        schools = obj.get_schools_by_status("1")  # Get active schools
        return jsonify({'status': 'success', 'message':'Successfully get active schools','data': schools}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/school/update_status/<int:school_id>', methods=['PATCH'])
def update_school_status(school_id):
    """Update the status of a school."""
    data = request.json

    # Validate input
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400

    new_status = data['status']

    # Validate status value (it should be 0 or 1)
    if new_status not in [0, 1]:
        return jsonify({'error': 'Invalid status. Status must be either 0 (pending) or 1 (active).'}), 400

    try:
        # Update the school status in the database
        status_update_status = obj.update_school_status(school_id, new_status)

        if status_update_status['status']:
            return jsonify({'message': 'School status updated successfully'}), 200
        else:
            return jsonify({'error': status_update_status['message']}), 500
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


def send_email(email, school_id, password):
    """Send login details via email."""
    msg = Message(
        "Login Details for School Panel",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f"Your login details:\nSchool ID: {school_id}\nPassword: {password}\n"
    mail.send(msg)

def generate_md5(password):
    """Hash a password using MD5."""
    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Update the hash object with the bytes of the password
    md5_hash.update(password.encode('utf-8'))

    # Return the hexadecimal digest of the password
    return md5_hash.hexdigest()


if __name__ == '__main__':
    app.run(debug=True)