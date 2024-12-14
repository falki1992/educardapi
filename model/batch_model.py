import mysql.connector
from mysql.connector import Error
from config.config import dbconfig
from datetime import timedelta
import os


class batch_model:
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

    def create_batch(self, name, start_date, end_date, start_time, end_time, description, batch_image, no_of_student):
        """Create a new batch."""
        try:
            query = """
                INSERT INTO class
                (name, start_date, end_date, start_time, end_time, description, batch_image, no_of_student)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cur.execute(query, (name, start_date, end_date, start_time, end_time, description, batch_image, no_of_student))
            return self.cur.lastrowid
        except Error as e:
            return str(e)

    def get_all_batches(self):
        try:
            query = "SELECT * FROM class"  # Ensure the correct table name
            self.cur.execute(query)
            results = self.cur.fetchall()

            # Convert all non-serializable fields to JSON-friendly formats
            for record in results:
                if isinstance(record.get('start_time'), timedelta):
                    record['start_time'] = str(record['start_time'])
                if isinstance(record.get('end_time'), timedelta):
                    record['end_time'] = str(record['end_time'])

            return results
        except Error as e:
            return str(e)

    def get_batch_by_id(self, batch_id):
        """Fetch a single batch by ID."""
        try:
            query = "SELECT * FROM class WHERE id = %s"
            self.cur.execute(query, (batch_id,))
            result = self.cur.fetchone()

            # Convert `timedelta` to a string or seconds (for JSON serialization)
            if result:
                if isinstance(result.get('start_time'), timedelta):
                    result['start_time'] = str(result['start_time'])
                if isinstance(result.get('end_time'), timedelta):
                    result['end_time'] = str(result['end_time'])

            return result
        except Error as e:
            return str(e)

    def update_batch(self, batch_id, name, start_date, end_date, start_time, end_time, description, batch_image, no_of_student):
        """Update an existing batch."""
        try:
            query = """
                UPDATE class
                SET name = %s, start_date = %s, end_date = %s, start_time = %s, end_time = %s,
                    description = %s, batch_image = %s, no_of_student = %s
                WHERE id = %s
            """
            self.cur.execute(query, (name, start_date, end_date, start_time, end_time, description, batch_image, no_of_student, batch_id))
            return self.cur.rowcount
        except Error as e:
            return str(e)

    def delete_batch(self, batch_id):
        """Delete a batch."""
        try:
            query = "DELETE FROM class WHERE id = %s"
            self.cur.execute(query, (batch_id,))
            return self.cur.rowcount
        except Error as e:
            return str(e)

    def close_connection(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
