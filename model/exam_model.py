import mysql.connector
from mysql.connector import Error
from datetime import date
from config.config import dbconfig
import os


class exam_model:
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


    def fetch_exam(self, uid):
        """Fetch exam data."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor
        cursor.execute("""
            SELECT id, name
            FROM exams
            WHERE admin_id = %s AND type = 1 AND mock_sheduled_date <= %s
            ORDER BY id DESC LIMIT 1
        """, (uid, date.today()))
        exam = cursor.fetchone()
        cursor.close()
        return exam

    def fetch_batches(self):
        """Fetch all batches."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor
        cursor.execute("""
            SELECT id, batch_name
            FROM batches
            WHERE status = 1
            ORDER BY id DESC
        """)
        all_batches = cursor.fetchall()
        cursor.close()
        return all_batches

    def fetch_top_three_results(self, exam_id):
        """Fetch the top three results for an exam."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor
        cursor.execute("""
            SELECT mr.*, s.*
            FROM mock_result mr
            JOIN students s ON s.id = mr.student_id
            WHERE mr.paper_id = %s AND mr.percentage > 0
            ORDER BY mr.percentage DESC LIMIT 3
        """, (exam_id,))
        top_three = cursor.fetchall()
        cursor.close()
        return top_three

    def fetch_result_counts(self, exam_id):
        """Fetch counts of good, poor, and average results."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor

        cursor.execute("""
            SELECT COUNT(*) AS good_count
            FROM mock_result
            WHERE paper_id = %s AND percentage >= 80
        """, (exam_id,))
        good = cursor.fetchone()['good_count']

        cursor.execute("""
            SELECT COUNT(*) AS poor_count
            FROM mock_result
            WHERE paper_id = %s AND percentage < 60
        """, (exam_id,))
        poor = cursor.fetchone()['poor_count']

        cursor.execute("""
            SELECT COUNT(*) AS average_count
            FROM mock_result
            WHERE paper_id = %s AND percentage BETWEEN 60 AND 79
        """, (exam_id,))
        average = cursor.fetchone()['average_count']

        cursor.close()
        return good, poor, average

    def fetch_doubts_data(self):
        """Fetch counts of all doubts, approved doubts, and pending doubts."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor

        cursor.execute("SELECT COUNT(*) AS total_doubts FROM student_doubts_class")
        total_doubts = cursor.fetchone()['total_doubts']

        cursor.execute("""
            SELECT COUNT(*) AS approved_doubts
            FROM student_doubts_class
            WHERE status = 1
        """)
        approved_doubts = cursor.fetchone()['approved_doubts']

        cursor.execute("""
            SELECT COUNT(*) AS pending_doubts
            FROM student_doubts_class
            WHERE status = 0
        """)
        pending_doubts = cursor.fetchone()['pending_doubts']

        cursor.close()
        return total_doubts, approved_doubts, pending_doubts

    def fetch_payment_statistics(self, uid):
        """Fetch payment statistics (offline, online, and total amount)."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor

        cursor.execute("""
            SELECT SUM(amount) AS total_amount
            FROM student_payment_history
            WHERE admin_id = %s
        """, (uid,))
        total_amount = cursor.fetchone()['total_amount']

        cursor.execute("""
            SELECT COUNT(*) AS offline_payments
            FROM student_payment_history
            WHERE admin_id = %s AND mode = 'offline'
        """, (uid,))
        offline = cursor.fetchone()['offline_payments']

        cursor.execute("""
            SELECT COUNT(*) AS online_payments
            FROM student_payment_history
            WHERE admin_id = %s AND mode != 'offline'
        """, (uid,))
        online = cursor.fetchone()['online_payments']

        cursor.close()
        return total_amount, offline, online

    def fetch_all_users(self):
        """Fetch all users (excluding super admins)."""
        cursor = self.con.cursor(dictionary=True)  # Corrected from sor to cursor
        cursor.execute("""
            SELECT id, name, role
            FROM users
            WHERE super_admin = 0 AND role = 1
            ORDER BY id DESC
        """)
        all_users = cursor.fetchall()
        cursor.close()
        return all_users
