from app import app
from flask import request, jsonify
from model.user_model import user_model
from model.role_model import role_model
import hashlib
import os


# Initialize the user_model once as `obj`
obj = user_model()
roleObj = role_model()

@app.route("/user/getall")
def user_getAll_controller():
    return obj.all_user_model()

@app.route('/user/create', methods=['POST'])
def register_user():
    data = request.json

    # Validate incoming data
    required_fields = ['name', 'email', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'name, email, password, and role are required'}), 400

    name = data['name']
    email = data['email']
    password = data['password']
    role = data['role']

    # Fetch the role ID by name
    role_id = roleObj.get_role_id_by_name(role)  # Replace with your function to fetch role ID
    if isinstance(role_id, str):  # Error occurred
        return jsonify({'error': role_id}), 500
    if not role_id:  # Invalid role name
        return jsonify({'error': 'Invalid role'}), 400

    # Check if user already exists
    existing_user = obj.get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    # Securely hash the password using scrypt
    password_hash = generate_md5(password)

    # Insert new user with role ID
    user_id = obj.insert_user(name, email, password_hash, role_id)
    if isinstance(user_id, str):  # If an error occurred during insert
        return jsonify({'error': user_id}), 500

    return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201




def generate_md5(password):
    """Hash a password using MD5."""
    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Update the hash object with the bytes of the password
    md5_hash.update(password.encode('utf-8'))

    # Return the hexadecimal digest of the password
    return md5_hash.hexdigest()


