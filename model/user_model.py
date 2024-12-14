from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from flask import jsonify
from werkzeug.security import generate_password_hash
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from a `.env` file
load_dotenv()

class user_model:
    def __init__(self):
        """Initialize the database connection."""
        try:
            # Fetch database configuration from environment variables
            self.db_config = {
                'host': os.getenv('DB_HOST', ''),
                'user': os.getenv('DB_USER', ''),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', ''),
                'port': int(os.getenv('DB_PORT', 3306)),  # Default MySQL port
            }

            # Connect to the database
            self.con = mysql.connector.connect(**self.db_config)
            self.cur = self.con.cursor(dictionary=True)  # Enable dictionary cursor

            if self.con.is_connected():
                print("Secure database connection established.")
        except Error as e:
            print("Error connecting to the database. Check logs for details.")
            with open('db_error.log', 'a') as log_file:
                log_file.write(f"Database Error: {str(e)}\n")
            self.con = None
            self.cur = None

    def all_user_model(self):
        """Fetch all users from the database."""
        try:
            self.cur.execute("SELECT * FROM users")
            result = self.cur.fetchall()
            if result:
                return jsonify({"payload": result}), 200
            else:
                return jsonify({"message": "No Data Found"}), 404
        except Error as e:
            return jsonify({"error": str(e)}), 500

    def get_user_by_email(self, email):
        """Fetch a user by email."""
        try:
            query = "SELECT * FROM users WHERE email = %s"
            self.cur.execute(query, (email,))
            return self.cur.fetchone()
        except Error as e:
            return None

    def insert_user(self, name, email, password, role):
        """Insert a new user into the database."""
        try:
            hashed_password = self.hash_password(password)
            query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
            self.cur.execute(query, (name, email, hashed_password, role))
            self.con.commit()
            return self.cur.lastrowid
        except Error as e:
            return str(e)

    # Login Functions
    def find_user_by_email(self, email):
        """Fetch user by email if status=1."""
        try:
            query = """
            SELECT * FROM users
            WHERE email = %s AND status = 1
            """
            self.cur.execute(query, (email,))
            return self.cur.fetchone()
        except Error as e:
            return None

    def hash_password(self, password):
        """Hash the password using MD5."""
        md5_hash = hashlib.md5()
        md5_hash.update(password.encode('utf-8'))
        return md5_hash.hexdigest()

    def verify_password(self, input_password, stored_password):
        """Verify the input password with the stored MD5 hashed password."""
        hashed_input = self.hash_password(input_password)
        return hashed_input == stored_password

    def login_user(self, email, password):
        """Handle user login logic."""
        try:
            user = self.find_user_by_email(email)
            if not user:
                return {'status': 'FAILED', 'message': 'User not found or unauthorized'}

            if self.verify_password(password, user['password']):
                role_id = user['role']
                user['user_role'] = self.get_role_by_id(role_id)
                return {'status': 'OK', 'message': 'Login successful', 'response': user}
            else:
                return {'status': 'FAILED', 'message': 'Invalid credentials'}
        except Error as e:
            return {'status': 'ERROR', 'message': str(e)}

    def update_token(self, user_id, token):
        """Update the token field in the users table."""
        try:
            query = """
            UPDATE users
            SET token = %s
            WHERE id = %s
            """
            self.cur.execute(query, (token, user_id))
            self.con.commit()
            print(f"Token updated successfully for user_id: {user_id}")
        except Error as e:
            return str(e)

    def verify_token(self, token):
        """Verify if the provided token is valid."""
        try:
            query = """
            SELECT id, email FROM users
            WHERE token = %s
            """
            self.cur.execute(query, (token,))
            return self.cur.fetchone()  # Return user details if token is valid
        except Error as e:
            print(f"Error verifying token: {e}")
            return None

    def get_role_by_id(self, role_id):
        """Fetch role name by role ID."""
        try:
            query = "SELECT id, name FROM roles WHERE id = %s"
            self.cur.execute(query, (role_id,))
            result = self.cur.fetchone()
            if result:
                return result['name']
            return None
        except Error as e:
            return str(e)

    def close_connection(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
