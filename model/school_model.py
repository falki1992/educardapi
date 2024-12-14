from datetime import datetime
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import dbconfig
import os


class school_model:
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




    def find_school_by_email_or_id(self, email, school_id):
        """Check if a school exists by email or school_id."""
        try:
            query = "SELECT * FROM schools WHERE email = %s OR school_uuid = %s"
            self.cur.execute(query, (email, school_id))
            return self.cur.fetchone()
        except Error as e:
            print(f"Error fetching school: {e}")
            return None

    def hash_password(self, password):
        """Hash a password."""
        return generate_password_hash(password)

    def register_school(self, school_name, principal_name, school_id, password_hash, email, mobile_number, created_by):
        """Register a new school in the database."""
        try:
            query = """
                INSERT INTO schools (name, principal_name, school_uuid, password, email, mobile_number, created_at, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cur.execute(query, (school_name, principal_name, school_id, password_hash, email, mobile_number, datetime.utcnow(), created_by))
            return {'status': True}
        except Error as e:
            print(f"Error registering school: {e}")
            return {'status': False, 'message': str(e)}

    def get_schools_by_status(self, status):
        """Fetch schools based on their status."""
        try:
            if status is None:  # Fetch all schools
                query = "SELECT id, name, principal_name, school_uuid, status,email,mobile_number FROM schools"
                self.cur.execute(query)
            else:  # Fetch schools by specific status
                query = "SELECT id, name, principal_name, school_uuid, status,email,mobile_number FROM schools WHERE status = %s"
                self.cur.execute(query, (status,))

            results = self.cur.fetchall()
            return results  # Return all matching records
        except Error as e:
            print(f"Database error: {e}")
            return str(e)
    def update_school_status(self, school_id, new_status):
        """Update the status of a school in the database."""
        try:
            query = """
                UPDATE schools
                SET status = %s
                WHERE id = %s
            """
            self.cur.execute(query, (new_status, school_id))

            if self.cur.rowcount > 0:  # If the school was found and updated
                return {'status': True}
            else:
                return {'status': False, 'message': 'School not found or no change in status'}
        except Error as e:
            print(f"Error updating school status: {e}")
            return {'status': False, 'message': str(e)}


    def close_connection(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
