import mysql.connector
from mysql.connector import Error
from datetime import date
from config.config import dbconfig
from datetime import datetime

class notice_model:
    def __init__(self):
        try:
            self.con = mysql.connector.connect(
                host=dbconfig['host'],
                user=dbconfig['username'],
                password=dbconfig['password'],
                database=dbconfig['database']
            )
            self.con.autocommit = True
            self.cur = self.con.cursor(dictionary=True)
        except Error as e:
            print(f"Database connection error: {e}")
            self.con = None

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
