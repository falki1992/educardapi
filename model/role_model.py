import mysql.connector
from mysql.connector import Error
from config.config import dbconfig

class role_model:
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

    def get_all_roles(self):
        try:
            query = "SELECT id, name FROM roles"
            self.cur.execute(query)
            roles = self.cur.fetchall()
            return roles
        except Exception as e:
            print(f"Error fetching roles: {e}")
            return []
    def get_role_by_id(self, role_id):
        try:
            query = "SELECT * FROM roles WHERE id = %s"
            self.cur.execute(query, (role_id,))
            role = self.cur.fetchone()
            return role if role else None
        except Error as e:
            print(f"Error fetching role by ID: {e}")
            return None

    def create_role(self, name):
        if not self.con:
            print("No database connection available.")
            return None
        try:
            query = "INSERT INTO roles (name) VALUES (%s)"
            self.cur.execute(query, (name,))
            self.con.commit()  # Commit the transaction
            return self.cur.lastrowid  # Return the ID of the inserted row
        except Error as e:
            print(f"Error creating role: {e}")
            return None


    def update_role(self, role_id, name):
        try:
            query = "UPDATE roles SET name = %s WHERE id = %s"
            self.cur.execute(query, (name, role_id))
            return self.cur.rowcount  # Returns number of rows affected
        except Error as e:
            print(f"Error updating role: {e}")
            return None

    def delete_role(self, role_id):
        try:
            query = "DELETE FROM roles WHERE id = %s"
            self.cur.execute(query, (role_id,))
            return self.cur.rowcount
        except Error as e:
            print(f"Error deleting role: {e}")
            return None


    def get_role_id_by_name(self, role_name):
        try:
            query = "SELECT id,name FROM roles WHERE name = %s"
            self.cur.execute(query, (role_name,))
            result = self.cur.fetchone()

            if result:
                return result['id']
            else:
                return None  # No such role found
        except Error as e:
            return str(e)




    def close(self):
        self.cur.close()
