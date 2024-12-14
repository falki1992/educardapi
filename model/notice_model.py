import mysql.connector
from mysql.connector import Error
from datetime import date
from config.config import dbconfig
from datetime import datetime
import os

class notice_model:
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

    def create_notice(self, title, description, status, date, variable, added_by):
        """
        Insert a new notice into the database.
        """
        try:
            query = """
                INSERT INTO notices (title, description, status, date, variable, added_by, added_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            created_at = datetime.utcnow()
            self.cur.execute(query, (title, description, status, date, variable, added_by, created_at))
            self.con.commit()

            return {'status': 'OK', 'message': 'Notice created successfully'}
        except Error as e:
            print(f"Error creating notice: {e}")
            return {'status': 'FAILED', 'message': str(e)}

    def get_notices_by_variable(self, variable):
        """
        Fetch notices based on the variable.
        """
        try:
            query = """
                SELECT id, title, description, status, date, variable, added_by, added_at
                FROM notices
                WHERE variable = %s OR variable = 'all'
                ORDER BY added_at DESC
            """
            self.cur.execute(query, (variable,))
            notices = self.cur.fetchall()
            return {'status': 'OK', 'message': 'Notices fetched successfully', 'data': notices}
        except Error as e:
            print(f"Error fetching notices: {e}")
            return {'status': False, 'message': str(e)}


    def close_connection(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
