from app import app
from flask import request, jsonify,session
from model.user_model import user_model
import uuid
from datetime import datetime, timedelta


# Set a secret key for secure sessions
app.secret_key = '312cd53f49c08f293d0d4ffa43ac08fe'  # Replace with a unique and secret value

# Initialize the user_model once as `obj`
obj = user_model()

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status': 'FAILED', 'message': 'Email and password are required'}), 400

        # Attempt to log in the user
        response = obj.login_user(email, password)
        if response['status'] == 'OK':
            # Generate a token (e.g., using UUID)
            token = str(uuid.uuid4())  # Unique token
            user_id = response['response']['id']


            # Set expiration time (e.g., 2 hours from now)
            expiration_time = datetime.utcnow() + timedelta(hours=2)

            # Store the token in the users table
            obj.update_token(user_id, token)

            return jsonify(response), 200
        else:
            return jsonify({'status': 'FAILED', 'message': 'Invalid email or password'}), 400
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Error during login: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
