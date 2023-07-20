import schedule
import time
import logging
from openIdGetter import OpenidGetter
from databaseManager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def job():
    logger.info("Starting job")
    appid = 'wxa31121df217466fd'
    secret = '23f9655e97542d4230a1ac9eea819ee7'
    getter = OpenidGetter(appid, secret)
    db_manager = DatabaseManager(host='127.0.0.1', database='myaccount', user='root', password='mysql@123', pool_size=5)
    while True:
        logger.info("Getting openids")
        openids = getter.get_openids()
        logger.info(f"Got {len(openids)} openids")
        for openid in openids:
            logger.info(f"Inserting openid {openid}")
            db_manager.insert_user_balance(openid, balance=0)  # Assuming you start with a balance of 0
            db_manager.insert_user_status(openid, status=1)  # Assuming you start with a status of 1
        if not getter.next_openid:
            logger.info("No more openids")
            break  # stop if there are no more openids
            db_manager.insert_user_balance_and_status(openid)
    else:
        logger.info("No more openids")
    logger.info("Job finished")

# Schedule the job every hour
schedule.every(1).hours.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)

