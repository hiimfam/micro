import connexion
from connexion import NoContent
import json
import datetime
import mysql.connector
import pymysql
import yaml
import logging
import logging.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from base import Base
from artists import addArtist
from songs import addSong

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    user = app_config["datastore"]["user"]
    password = app_config["datastore"]["password"]
    hostname = app_config["datastore"]["hostname"]
    port = app_config["datastore"]["port"]
    db = app_config["datastore"]["db"]

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config) 

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(user, password, hostname, port, db))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("Connecting to DB. Hostname: william-micro.eastus2.cloudapp.azure.com, Port: 3306")

def report_add_artist(body):
    """Recieves an artist"""

    session = DB_SESSION()

    artist = addArtist(body["artist_id"], body["artist_name"], body["username"], body["albums_recorded"], body['trace_id'])
                    
    session.add(artist)

    session.commit()

    session.close()

    received_event = "Stored event {} request with a trace id of {}".format("Report Artist Posted", body['trace_id'])
    logger.debug(received_event)



def report_add_song(body):
    """Recieves a song"""

    session = DB_SESSION()

    song = addSong(body["name"], body["song_length"], body["username"], body["released_date"], body['trace_id'])
    
    received_event = "Stored event {} request with a trace id of {}".format("Report Song Posted", body['trace_id'])
    logger.debug(received_event)

    session.add(song)

    session.commit()
    
    session.close()


def get_add_artist(timestamp):
    """ Gets new artist """

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(addArtist).filter(addArtist.date_created >= timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for add song in readings after %s returns %d results" %
                (timestamp, len(results_list)))

    return results_list, 200


def get_add_song(timestamp):
    """ Gets new song """

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(addSong).filter(addSong.date_created >= timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for add song readings after %s returns %d results" %
                (timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname1 = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname1)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consumer on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "artists":  # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            logger.info("Storing artist event")
            report_add_artist(payload)
        elif msg["type"] == "songs":  # Change this to your event type
        # Store the event2 (i.e., the payload) to the DB
            logger.info("Storing song event")
            report_add_song(payload)

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)