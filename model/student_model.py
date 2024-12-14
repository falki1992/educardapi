from datetime import datetime
import random
import mysql.connector
from mysql.connector import Error
from config.config import dbconfig
from werkzeug.security import generate_password_hash
import os


class student_model:
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


    def validate_input(self, data):
        return all([data.get('name'), data.get('email'), data.get('mobile')])

    def check_existing_student(self, email, mobile):
        query = "SELECT id FROM students WHERE email = %s AND contact_no = %s"
        self.cur.execute(query, (email, mobile))
        return self.cur.fetchone()

    def get_batch_info(self, batch_id):
        if not batch_id:
            return None  # Or return an error if batch_id is mandatory
        query = "SELECT admin_id, batch_name, batch_type FROM batches WHERE id = %s"
        self.cur.execute(query, (batch_id,))
        return self.cur.fetchone()

    def register_student(self, data):
        if not self.validate_input(data):
            return {'status': 'false', 'msg': 'Missing required parameters'}

        if self.check_existing_student(data['email'], data['mobile']):
            return {'status': 'false', 'msg': 'Email or mobile already registered'}

        batch_info = self.get_batch_info(data['batch_id'])
        admin_id = batch_info['admin_id'] if batch_info else 0
        enrollment_id = f"ENROLL{admin_id}{random.randint(10, 100)}"
        password = f"PASS{admin_id}{random.randint(1000, 5000)}"
        hashed_password = generate_password_hash(password)

        student_insert_query = """
            INSERT INTO students
            (name, email, batch_id, added_by, status, enrollment_id, password, admission_date, image, contact_no, login_status, last_login_app, app_version, token, admin_id)
            VALUES (%s, %s, %s, 'student', 1, %s, %s, %s, 'student_img.png', %s, 1, %s, %s, %s, %s)
        """
        admission_date = datetime.now().strftime('%Y-%m-%d')
        last_login_app = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cur.execute(student_insert_query, (
            data['name'], data['email'], data['batch_id'], enrollment_id, hashed_password,
            admission_date, data['mobile'], last_login_app, data.get('versionCode', ''),
            data.get('token', ''), admin_id
        ))
        student_id = self.cur.lastrowid

        if batch_info and batch_info['batch_type'] == 2:
            self.process_payment(student_id, data, admin_id)

        self.cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student_data = self.cur.fetchone()
        if student_data:
            student_data['password'] = password
            return {'status': 'true', 'msg': 'Account created successfully', 'data': student_data}
        else:
            return {'status': 'false', 'msg': 'Error retrieving student data'}

    def process_payment(self, student_id, data, admin_id):
        payment_query = """
            INSERT INTO student_payment_history (student_id, batch_id, transaction_id, amount, admin_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cur.execute(payment_query, (
            student_id, data['batch_id'], data.get('transaction_id', ''),
            data.get('amount', ''), admin_id
        ))
    def close(self):
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()