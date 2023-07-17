import schedule
import time
import logging
from openIdGetter import OpenidGetter
from db_manager import DatabaseManager
from log import logger
def job():
    logger.info("Starting job")
    appid = 'wxa31121df217466fd'
    secret = '23f9655e97542d4230a1ac9eea819ee7'
    getter = OpenidGetter(appid, secret)
    db_manager = DatabaseManager()
    logger.info("Getting openids")
    openids = getter.get_openids()
    logger.info("此处调用get_openids")
    logger.info(f"Got {len(openids) if openids else 0} openids")
    if not openids:
        for openid in openids:
            logger.info(f"Inserting openid {openid}")
            db_manager.insert_user_balance(openid)
            db_manager.insert_user_status(openid)
    else:
        logger.info("No more openids")
    logger.info("Job finished")

# Schedule the job every minute
schedule.every(1).minutes.do(job)


# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)

