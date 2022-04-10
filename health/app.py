import requests
import connexion
import yaml
import logging
import logging.config
import datetime
import json
import time
from pykafka import KafkaClient
from connexion import NoContent
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from healths import Health
from sqlalchemy.orm import sessionmaker
from base import Base
from flask_cors import CORS, cross_origin
import os
import sqlite3
from time import sleep


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')



DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def populate_health():
    logger.info("Start Periodic Health Check")

    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_update.desc()).first()
    session.close()

    if not results:
        health = {
            "receiver": "Running",
            "storage": "Down",
            "processing": "Running",
            "audit": "Running",
            "last_update": "2016-08-29T09:12:33Z"
        }
    else:
        health = results.to_dict()

    retry_count = 0
    """ Process event messages """ 
     
                    
    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            get_receiver_health = requests.get(app_config["receiver"]["url"], timeout=5)
            logger.info('trying to connect, attempt: %d' % (retry_count))
            print(get_receiver_health)
            if get_receiver_health.status_code == 200:
                logger.info("Receiver is running with a status code of {}".format(get_receiver_health.status_code))
                receiver_status = "Running"
                health['receiver_status'] = receiver_status
        except:
            logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
            retry_count += 1
            logger.error("Receiver is not running.")
            receiver_status = "Down"
            health['receiver_status'] = receiver_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break


     
    retry_count = 0
    """ Process event messages """ 
    
                    
    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            get_storage_health = requests.get(app_config["storage"]["url"], timeout=5) 
            logger.info('trying to connect, attempt: %d' % (retry_count))
            print(get_storage_health)
            if get_storage_health.status_code == 200:
                logger.info("Storage is running with a status code of {}".format(get_storage_health.status_code))
                storage_status = "Running"
                health['storage_status'] = storage_status
        except:
            logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
            retry_count += 1
            logger.error("Storage is not running.")
            storage_status = "Down"
            health['storage_status'] = storage_status
            sleep(app_config["kafka_connect"]["sleep_time"])
            
        else:
            break

    
    retry_count = 0

    """ Process event messages """ 
    
    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            get_processing_health = requests.get(app_config["processing"]["url"], timeout=5) 
            logger.info('trying to connect, attempt: %d' % (retry_count))
            print(get_processing_health)
            if get_processing_health.status_code == 200:
                logger.info("Processing is running with a status code of {}".format(get_processing_health.status_code))
                processing_status = "Running"
                health['processing_status'] = processing_status
        except:
            logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
            retry_count += 1
            logger.error("Processing is not running.")
            processing_status = "Down"
            health['processing_status'] = processing_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break

    retry_count = 0

    """ Process event messages """ 
    
                    
    while retry_count < app_config["kafka_connect"]["retry_count"]:
        try:
            get_audit_health = requests.get(app_config["audit_log"]["url"], timeout=5) 
            logger.info('trying to connect, attempt: %d' % (retry_count))
            print(get_audit_health)
            if get_audit_health.status_code == 200:
                logger.info("Audit is running with a status code of {}".format(get_audit_health.status_code))
                audit_status = "Running"
                health['audit_status'] = audit_status
        except:
            logger.info('attempt %d failed, retry in 5 seoncds' % (retry_count))
            retry_count += 1
            logger.error("Audit is not running.")
            audit_status = "Down"
            health['audit_status'] = audit_status
            sleep(app_config["kafka_connect"]["sleep_time"])
        else:
            break
   
   
    timestamp = datetime.datetime.now()
    current_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    session = DB_SESSION()

    health_new = Health(health["receiver_status"],
                      health["storage_status"],
                      health["processing_status"],
                      health["audit_status"],
                      timestamp)

    session.add(health_new)

    session.commit()
    session.close()


def get_health():
    logger.info("Request has started")

    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_update.desc()).first()
    session.close()

    if not results:
        health = {
            "receiver": "Running",
            "storage": "Down",
            "processing": "Running",
            "audit": "Running",
            "last_update": "2016-08-29T09:12:33Z"
        }
    else:
        health = results.to_dict()

    logger.debug(health)

    logger.info("Request has completed")

    return health, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("healthapi.yml", strict_validation=True, validate_responses=True)



if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)