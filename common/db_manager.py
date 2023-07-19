
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
from common.log import logger

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseManager(metaclass=Singleton):
    def __init__(self, host='127.0.0.1', database='myaccount', user='root', password='mysql@123', pool_size=25):
        dbconfig = {
            "host": host,
            "user": user,
            "passwd": password,
            "database": database,
        }
        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_size=pool_size, **dbconfig)

    def insert_usage_record(self, contextType, model, completion_tokens, session_id):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # Create insert statement
        add_usage_record = ("INSERT INTO usage_records "
                            "(usage_time, type, model, token_length, openid) "
                            "VALUES (%s, %s, %s, %s, %s)")

        # Insert new usage record
        data_usage_record = (datetime.now(), contextType, model, completion_tokens, session_id)
        cursor.execute(add_usage_record, data_usage_record)

        # Commit the changes
        cnx.commit()

        # Close cursor and connection
        cursor.close()
        cnx.close()

    def insert_user_balance(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # Create insert statement
        add_openid = "INSERT IGNORE  INTO user_balance (openid, balance) VALUES (%s, 100000)"

        # Insert new openid
        data_openid = (openid,)
        cursor.execute(add_openid, data_openid)

        # Commit the changes
        cnx.commit()

        # Close cursor and connection
        cursor.close()
        cnx.close()

    def insert_user_status(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # Create insert statement
        add_openid = "INSERT IGNORE  INTO user_status (openid, usage_status) VALUES (%s, 1)"

        # Insert new openid
        data_openid = (openid,)
        cursor.execute(add_openid, data_openid)

        # Commit the changes
        cnx.commit()

        # Close cursor and connection
        cursor.close()
        cnx.close()

    def check_usage_status(self, session_id):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # SQL query to retrieve the value from the user_status table
        sql = "SELECT usage_status FROM user_status WHERE openid = %s"
        cursor.execute(sql, (session_id,))

        # Fetch the result
        result = cursor.fetchone()

        # Close cursor and connection
        cursor.close()
        cnx.close()

        # If result is None, that means the session_id does not exist in the database
        if result is None:
            raise ValueError("Invalid session_id")

        # Convert the result to bool and return
        return bool(result[0])

    def deduct_balance(self, openid, token_length):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()
        try:
            sql_get_balance = "SELECT balance FROM user_balance WHERE openid=%s FOR UPDATE"
            cursor.execute(sql_get_balance, (openid,))
            result = cursor.fetchone()
            if result is None:
                logger.info(f"Openid {openid} not found in user_balance.")
                return
            current_balance = result[0]

            new_balance = current_balance - token_length
            if new_balance < 0:
                logger.info(f"Insufficient balance for openid {openid}.")
                self.update_usage_status(openid,0)
                return

            sql_update_balance = "UPDATE user_balance SET balance=%s WHERE openid=%s"
            cursor.execute(sql_update_balance, (new_balance, openid))

            cnx.commit()
            logger.info(f"Deducted {token_length} from openid {openid}. New balance: {new_balance}")
        except Exception as e:
            cnx.rollback()
            logger.info(f"Failed to deduct balance for openid {openid}. Error: {e}")
        finally:
            cursor.close()
    def update_usage_status(self, openid,status):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # SQL query to update the value in the user_status table
        sql = "UPDATE usage_status SET usage_status = %s WHERE openid = %s"
        cursor.execute(sql, (openid,status))

        # Commit the change
        cnx.commit()

        # Close cursor and connection
        cursor.close()
        cnx.close()