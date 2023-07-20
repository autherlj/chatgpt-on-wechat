
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
    def __init__(self, host='127.0.0.1', database='myaccount', user='root', password='mysql@123', pool_size=50):
        dbconfig = {
            "host": host,
            "user": user,
            "passwd": password,
            "database": database,
        }
        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_size=pool_size, **dbconfig)

    def insert_user_balance_and_status(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        try:
            # Create insert statement for user_balance
            add_openid_balance = "INSERT IGNORE INTO user_balance (openid, balance) VALUES (%s, 100000)"

            # Insert new openid to user_balance
            data_openid_balance = (openid,)
            cursor.execute(add_openid_balance, data_openid_balance)

            # Create insert statement for user_status
            add_openid_status = "INSERT IGNORE INTO user_status (openid, usage_status) VALUES (%s, 1)"

            # Insert new openid to user_status
            data_openid_status = (openid,)
            cursor.execute(add_openid_status, data_openid_status)

            # Commit the changes
            cnx.commit()
        except Exception as e:
            # If an error occurs, roll back the transaction
            cnx.rollback()
            logger.error(f"Failed to insert balance and status for openid {openid}. Error: {e}")
        finally:
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

    def deduct_balance(self, context_type, model, openid, token_length):
        # 参数校验
        if not openid or token_length <= 0:
            logger.error(f"Invalid parameters. openid: {openid}, token_length: {token_length}")
            return

        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        try:
            cursor = cnx.cursor()

            # 明确地开始事务
            cnx.start_transaction()

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
                sql = "UPDATE usage_status SET usage_status = %s WHERE openid = %s"
                cursor.execute(sql, (0, openid))
            else:
                sql_update_balance = "UPDATE user_balance SET balance=%s WHERE openid=%s"
                cursor.execute(sql_update_balance, (new_balance, openid))

                add_usage_record = ("INSERT INTO usage_records "
                                    "(usage_time, type, model, token_length, openid) "
                                    "VALUES (%s, %s, %s, %s, %s)")
                data_usage_record = (datetime.now(), context_type, model, token_length, openid)
                cursor.execute(add_usage_record, data_usage_record)

                logger.info(f"Deducted {token_length} from openid {openid}. New balance: {new_balance}")

            # 提交事务
            cnx.commit()
        except Exception as e:
            # 发生错误时回滚事务
            cnx.rollback()
            logger.error(f"Failed to deduct balance for openid {openid}. Error: {e}")
            raise
        finally:
            # 关闭游标和连接
            cursor.close()
            cnx.close()
