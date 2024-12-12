from datetime import datetime
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import dbconfig
from datetime import timedelta


class membership_model:
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

    def create_plan(self, name, description, price, duration_months):
        """
        Insert a new membership plan into the database and return its details.
        """
        try:
            query = """
                INSERT INTO memberships (name, description, price, duration_months, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            created_at = datetime.utcnow()
            self.cur.execute(query, (name, description, price, duration_months, created_at))
            self.con.commit()

            # Fetch the full details of the newly created plan
            last_inserted_id = self.cur.lastrowid

            select_query = "SELECT * FROM memberships WHERE id = %s"
            self.cur.execute(select_query, (last_inserted_id,))
            plan_details = self.cur.fetchone()  # Fetch the single row as a dictionary

            return {'status': 'OK', 'message': 'Membership plan created successfully', 'response': plan_details}
        except Error as e:
            print(f"Error creating membership plan: {e}")
            return {'status': False, 'message': str(e)}



    def get_all_plans(self):
        """
        Fetch all membership plans from the database.
        """
        try:
            query = "SELECT id, name, description, price, duration_months, created_at FROM memberships"
            self.cur.execute(query)
            plans = self.cur.fetchall()
            return {'status': 'OK', 'message': 'Membership plans get successfully', 'response': plans}
        except Error as e:
            print(f"Error fetching membership plans: {e}")
            return {'status': False, 'message': str(e)}

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