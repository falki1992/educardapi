import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


class role_model:
    def __init__(self):
        """Initialize the database connection."""
        try:
            self.db_config = {
                'host': os.getenv('DB_HOST', ''),
                'user': os.getenv('DB_USER', ''),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', ''),
                'port': int(os.getenv('DB_PORT', 3306)),
            }
            self.con = mysql.connector.connect(**self.db_config)
            self.cur = self.con.cursor(dictionary=True)
            logging.info("Database connection established.")
        except Error as e:
            logging.error(f"Database connection error: {e}")
            self.con = None
            self.cur = None

    def get_all_roles(self):
        """Fetch all roles."""
        if not self.cur:
            logging.error("No database connection.")
            return None
        try:
            query = "SELECT id, name FROM roles"
            self.cur.execute(query)
            return self.cur.fetchall()
        except Error as e:
            logging.error(f"Error fetching roles: {e}")
            return None

    def get_role_by_id(self, role_id):
        """Fetch a role by its ID."""
        if not self.cur:
            logging.error("No database connection.")
            return None
        try:
            query = "SELECT * FROM roles WHERE id = %s"
            self.cur.execute(query, (role_id,))
            return self.cur.fetchone()
        except Error as e:
            logging.error(f"Error fetching role by ID: {e}")
            return None

    def create_role(self, name):
        """Create a new role."""
        if not self.cur:
            logging.error("No database connection.")
            return None
        try:
            query = "INSERT INTO roles (name) VALUES (%s)"
            self.cur.execute(query, (name,))
            self.con.commit()
            return self.cur.lastrowid
        except Error as e:
            self.con.rollback()
            logging.error(f"Error creating role: {e}")
            return None

    def update_role(self, role_id, name):
        """Update a role."""
        if not self.cur:
            logging.error("No database connection.")
            return None
        try:
            query = "UPDATE roles SET name = %s WHERE id = %s"
            self.cur.execute(query, (name, role_id))
            self.con.commit()
            return self.cur.rowcount
        except Error as e:
            self.con.rollback()
            logging.error(f"Error updating role: {e}")
            return None

    def delete_role(self, role_id):
        """Delete a role."""
        if not self.cur:
            logging.error("No database connection.")
            return None
        try:
            query = "DELETE FROM roles WHERE id = %s"
            self.cur.execute(query, (role_id,))
            self.con.commit()
            return self.cur.rowcount
        except Error as e:
            self.con.rollback()
            logging.error(f"Error deleting role: {e}")
            return None

    def close(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
        logging.info("Database connection closed.")
