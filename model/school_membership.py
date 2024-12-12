from datetime import datetime
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import dbconfig
from datetime import timedelta

class school_membership:
    def __init__(self):
        try:
            self.con = mysql.connector.connect(
                host=dbconfig['host'],
                user=dbconfig['username'],
                password=dbconfig['password'],
                database=dbconfig['database']
            )
            self.cur = self.con.cursor(dictionary=True)
        except Error as e:
            print(f"Database connection error: {e}")
            self.con = None

    def purchase_membership(self, school_id, membership_id, start_date):
        """
        Business logic to purchase a membership plan for a school.
        """
        try:
            # Fetch membership plan details
            query = "SELECT * FROM memberships WHERE id = %s"
            self.cur.execute(query, (membership_id,))
            membership_plan = self.cur.fetchone()

            if not membership_plan:
                return {'status': 'FAILED', 'message': 'Membership plan not found'}

            # Calculate end_date based on duration_months
            duration_months = membership_plan['duration_months']
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = start_date_obj + timedelta(days=30 * duration_months)

            # Insert purchase record into the school_memberships table
            insert_query = """
                INSERT INTO school_memberships (school_id, membership_id, start_date, end_date, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            created_at = datetime.utcnow()
            self.cur.execute(insert_query, (school_id, membership_id, start_date_obj, end_date_obj, created_at))

            return {
                'status': 'OK',
                'response': {
                    'school_id': school_id,
                    'membership_id': membership_id,
                    'start_date': start_date_obj.strftime("%Y-%m-%d"),
                    'end_date': end_date_obj.strftime("%Y-%m-%d"),
                    'price': membership_plan['price']
                }
            }
        except Error as e:
            print(f"Error purchasing membership: {e}")
            return {'status': 'FAILED', 'message': str(e)}

    def close_connection(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
