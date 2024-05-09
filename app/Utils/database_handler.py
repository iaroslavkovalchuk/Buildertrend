import mysql.connector
from app.Model.MainTable import MainTableModel, ProjectMessageModel
from datetime import datetime


class DatabaseHandler:
    def __init__(self, host='localhost', user='root', password='password', database='BuilderTrend'):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()
    # GET Main table data

    def get_main_table(self):
        sql = """ 
            SELECT A.id as customer_id, A.first_name, A.last_name, B.id AS id, B.claim_number, B.last_message, B.message_status, B.qued_timestamp, B.sent_timestamp, A.sending_method, A.email, A.phone, B.phone_sent_success, B.email_sent_success FROM
            (SELECT * FROM tbl_customer)A LEFT JOIN
            (SELECT * FROM tbl_project)B ON B.customer_id = A.id
        """
        # sql = """ 
        #     SELECT A.id as customer_id, A.first_name, A.last_name, B.id AS id, B.claim_number, B.last_message, B.message_status, B.qued_timestamp, B.sent_timestamp, A.sending_method FROM
        #     (SELECT * FROM tbl_customer)A LEFT JOIN
        #     (SELECT * FROM tbl_project)B ON B.customer_id = A.id
        # """
        self.cursor.execute(sql)
        project_list = self.cursor.fetchall()
        table_data = []
        for project in project_list:
            data_dict = dict(zip(MainTableModel.__fields__.keys(), project))
            table_data_instance = MainTableModel(**data_dict)
            table_data.append(table_data_instance)

        return table_data

    # CRUD Operations for tbl_customer
    # *********** using now ************
    def insert_customer(self, first_name="", last_name="", email="", phone="", address=""):
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
            sql_insert = "INSERT INTO tbl_customer (first_name, last_name, email, phone, address, send_method) VALUES (%s, %s, %s, %s, %s, %s)"
            val_insert = (first_name, last_name, email, phone, address, 1)
            self.cursor.execute(sql_insert, val_insert)
            self.db.commit()
            return self.cursor.lastrowid

    def get_customer_send_method(self, id):
        sql = "SELECT sending_method FROM tbl_customer WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

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
    def insert_message_history(self, message, project_id):
        sql = "INSERT INTO tbl_message_history (message, project_id, sent_time) VALUES (%s, %s, %s)"
        val = (message, project_id, datetime.utcnow())
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
        
    def check_duplicate_messgae(self, message):
        sql = "SELECT * FROM tbl_message_history WHERE message = %s"
        val = (message,)
        self.cursor.execute(sql, val)
        value = self.cursor.fetchall()
        return value.length != 0
    
    # CRUD Operations for tbl_project
    def insert_project(self, claim_number, customer_id):
        # Check if project already exists
        sql_check = "SELECT id FROM tbl_project WHERE claim_number = %s AND customer_id = %s AND project_name = %s"
        val_check = (claim_number, customer_id, claim_number)
        self.cursor.execute(sql_check, val_check)
        result = self.cursor.fetchone()

        if result is None:
            # If project does not exist, insert it
            sql_insert = "INSERT INTO tbl_project (claim_number, customer_id, project_name) VALUES (%s, %s, %s)"
            val_insert = (claim_number, customer_id, claim_number)
            self.cursor.execute(sql_insert, val_insert)
            self.db.commit()
            return self.cursor.lastrowid

    def get_project(self, id):
        sql = "SELECT * FROM tbl_project WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def get_all_projects(self):
        sql = "SELECT * FROM tbl_project"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_project(self, id, claim_number, project_name, last_message, message_status):
        sql = "UPDATE tbl_project SET claim_number = %s, project_name = %s, last_message = %s, message_status = %s WHERE id = %s"
        val = (claim_number, project_name, last_message, message_status, id)
        self.cursor.execute(sql, val)
        self.db.commit()
        
    def update_project_sent_status(self, id, phone_sent_success, email_sent_sucess):
        sql = "UPDATE tbl_project SET phone_sent_success = %s, email_sent_sucess = %s WHERE id = %s"
        val = (phone_sent_success, email_sent_sucess, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_project(self, id):
        sql = "DELETE FROM tbl_project WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()

    # CRUD Operations for tbl_report
    def insert_report(self, project_id, message="", timestamp=""):
        sql = "SELECT * FROM tbl_report WHERE project_id = %s AND message = %s AND timestamp = %s"
        val = (project_id, message, timestamp)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()

        if result is None:
            sql = "INSERT INTO tbl_report (project_id, message, timestamp) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.lastrowid

    def get_report(self, id):
        sql = "SELECT * FROM tbl_report WHERE project_id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchall()

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

    def get_user(self, username):
        sql = "SELECT * FROM tbl_user WHERE username = %s"
        val = (username,)
        self.cursor.execute(sql, val)
        return self.cursor.fetchone()

    def update_user(self, username, password, forgot_password_token):
        sql = "UPDATE tbl_user SET password = %s, forgot_password_token = %s WHERE username = %s"
        val = (password, forgot_password_token, username)
        self.cursor.execute(sql, val)
        self.db.commit()

    def delete_user(self, id):
        sql = "DELETE FROM tbl_user WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.db.commit()

    def update_sending_method(self, id, method):
        sql = "UPDATE tbl_customer SET sending_method = %s WHERE id = %s"
        val = (method, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def set_project_message(self, id, message):
        sql = "UPDATE tbl_project SET last_message = %s WHERE id = %s"
        val = (message, id)
        self.cursor.execute(sql, val)

    def set_project_status(self, id, message_status, qued_time):
        sql = "UPDATE tbl_project SET message_status = %s, qued_timestamp = %s WHERE id = %s"
        val = (message_status, qued_time, id)
        self.cursor.execute(sql, val)
        self.db.commit()
        
    def set_project_sent(self, id, message_status, sent_time):
        sql = "UPDATE tbl_project SET message_status = %s, sent_timestamp = %s WHERE id = %s"
        val = (message_status, sent_time, id)
        self.cursor.execute(sql, val)
        self.db.commit()

    def update_last_message(self, id, message):
        sql = "UPDATE tbl_project SET last_message = %s WHERE id = %s"
        val = (message, id)
        self.cursor.execute(sql, val)
        self.db.commit()


    def get_message_history_by_project_id(self, id):
        sql = "SELECT * FROM tbl_message_history WHERE project_id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        messages = self.cursor.fetchall()
        result = ''
        for message in messages:
            result += str(message[2]) + '\n' + \
                str(message[1]) + '\n---------------\n'
        return result.rstrip('---------------\n')


    def get_message_history_by_customer_id(self, id):
        sql = "SELECT * FROM tbl_project WHERE customer_id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        projects = self.cursor.fetchall()
        result = ''
        for project in projects:
            result += self.get_message_history_by_project_id(project[0])
        return result.rstrip('---------------\n')

    def close(self):
        self.db.close()
