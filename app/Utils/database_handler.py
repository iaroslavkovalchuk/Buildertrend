import mysql.connector

class DatabaseHandler:
    def __init__(self, host='sql3.freemysqlhosting.net', user='sql3698814', password='jxgCK4Ffjl', database='sql3698814'):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()

    # CRUD Operations for tbl_customer
    # *********** using now ************
    def insert_customer(self, first_name, last_name, email, phone, address):
        # Check if customer already exists
        sql_check = "SELECT id FROM tbl_customer WHERE first_name = %s AND last_name = %s AND email = %s AND phone = %s AND address = %s"
        val_check = (first_name, last_name, email, phone, address)
        self.cursor.execute(sql_check, val_check)
        result = self.cursor.fetchone()
        
        if result is not None:
            # If customer exists, return their ID
            return result[0]
        else:
            # If customer does not exist, insert them and return their ID
            sql_insert = "INSERT INTO tbl_customer (first_name, last_name, email, phone, address) VALUES (%s, %s, %s, %s, %s)"
            val_insert = (first_name, last_name, email, phone, address)
            self.cursor.execute(sql_insert, val_insert)
            self.db.commit()
            return self.cursor.lastrowid

    def get_customer(self, id):
        sql = "SELECT * FROM tbl_customer WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def update_customer(self, id, first_name, last_name, email, phone, address):
        sql = "UPDATE tbl_customer SET first_name = %s, last_name = %s, email = %s, phone = %s, address = %s WHERE id = %s"
        val = (first_name, last_name, email, phone, address, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_customer(self, id):
        sql = "DELETE FROM tbl_customer WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()

    # CRUD Operations for tbl_message_history
    def insert_message_history(self, id, message, project_id):
        sql = "INSERT INTO tbl_message_history (id, message, project_id) VALUES (%s, %s, %s)"
        val = (id, message, project_id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def get_message_history(self, id):
        sql = "SELECT * FROM tbl_message_history WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def update_message_history(self, id, message, project_id):
        sql = "UPDATE tbl_message_history SET message = %s, project_id = %s WHERE id = %s"
        val = (message, project_id, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_message_history(self, id):
        sql = "DELETE FROM tbl_message_history WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()

    # CRUD Operations for tbl_project
    def insert_project(self, claim_number, customer_id, project_name, last_message, message_status):
        # Check if project already exists
        sql_check = "SELECT id FROM tbl_project WHERE claim_number = %s AND customer_id = %s AND project_name = %s AND last_message = %s AND message_status = %s"
        val_check = (claim_number, customer_id, project_name, last_message, message_status)
        self.cursor.execute(sql_check, val_check)
        result = self.cursor.fetchone()

        if result is None:
            # If project does not exist, insert it
            sql_insert = "INSERT INTO tbl_project (claim_number, customer_id, project_name, last_message, message_status) VALUES (%s, %s, %s, %s, %s)"
            val_insert = (claim_number, customer_id, project_name, last_message, message_status)
            self.cursor.execute(sql_insert, val_insert)
            self.db.commit()

    def get_project(self, id):
        sql = "SELECT * FROM tbl_project WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def update_project(self, id, claim_number, customer_id, project_name, last_message, message_status):
        sql = "UPDATE tbl_project SET claim_number = %s, customer_id = %s, project_name = %s, last_message = %s, message_status = %s WHERE id = %s"
        val = (claim_number, customer_id, project_name, last_message, message_status, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_project(self, id):
        sql = "DELETE FROM tbl_project WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()

    # CRUD Operations for tbl_report
    def insert_report(self, project_id, message):
        sql = "INSERT INTO tbl_report (project_id, message) VALUES (%s, %s)"
        val = (project_id, message)
        self.cursor.execute(sql, val)
        self.db.commit()

    def get_report(self, id):
        sql = "SELECT * FROM tbl_report WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def update_report(self, id, project_id, message):
        sql = "UPDATE tbl_report SET project_id = %s, message = %s WHERE id = %s"
        val = (project_id, message, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_report(self, id):
        sql = "DELETE FROM tbl_report WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()

    # CRUD Operations for tbl_user
    def insert_user(self, username, password, forgot_password_token):
        sql = "INSERT INTO tbl_user (username, password, forgot_password_token) VALUES (%s, %s, %s)"
        val = (username, password, forgot_password_token)
        self.cursor.execute(sql, val)
        self.db.commit()

    def get_user(self, id):
        sql = "SELECT * FROM tbl_user WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def update_user(self, id, username, password, forgot_password_token):
        sql = "UPDATE tbl_user SET username = %s, password = %s, forgot_password_token = %s WHERE id = %s"
        val = (username, password, forgot_password_token, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_user(self, id):
        sql = "DELETE FROM tbl_user WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()
        
    def close(self):
        self.db.close()