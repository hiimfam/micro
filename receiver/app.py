import connexion
from connexion import NoContent
from pykafka import KafkaClient
import json
import datetime
import yaml
import requests
import logging.config
import logging
import random
from time import sleep


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    artist_url = app_config["Artist"]["url"]
    song_url = app_config["Songs"]["url"]
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    tp = app_config["events"]["topic"]

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

retry_count = 0

hostname = "%s:%d" % (app_config["events"]["hostname"],   
                        app_config["events"]["port"]) 

while retry_count < app_config["kafka_connect"]["retry_count"]:
    try:
        logger.info('trying to connect, attempt: %d' % (retry_count))
        print(hostname)
        client = KafkaClient(hosts=hostname) 
        topic = client.topics[str.encode(app_config['events']['topic'])] 
        producer = topic.get_sync_producer() 
    except:
        logger.info('attempt %d failed, retry in 5 seconds' % (retry_count))
        retry_count += 1
        sleep(app_config["kafka_connect"]["sleep_time"])
    else:
        break

logger.info('connected to kafka')

def addArtist(body):
    """Recieves an artist"""
    headers = {"content-type": "application/json"}
    trace_id = str(random.randint(0, 9999999999))
    event_name = artist_url.split("/")[-1]
    event_request = "Received event {} reading with a trace id of {}".format(event_name, trace_id)
    logger.info(event_request)
    body['trace_id'] = trace_id
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[str.encode(tp)]
    producer = topic.get_sync_producer()
    msg = {"type": "artists",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    returned_event = "Returned event {} reading response id:{} reading with status {}".format(event_name, trace_id, 201)
    logger.info(returned_event)

    return NoContent, 201


def addSong(body):
    """Recieves a song"""
    headers = {"content-type": "application/json"}
    trace_id = str(random.randint(0, 9999999999))
    event_name = song_url.split("/")[-1]
    event_request = "Received event {} reading with a trace id of {}".format(event_name, trace_id)
    logger.info(event_request)
    body['trace_id'] = trace_id
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[str.encode(tp)]
    producer = topic.get_sync_producer()
    msg = {"type": "songs",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    returned_event = "Returned event {} reading response id:{} reading with status {}".format(event_name, trace_id, 201)
    logger.info(returned_event)

    return NoContent, 201

def health():
    logger.info('Receiver service is running')

    return 200

app = connexion.FlaskApp(__name__, specification_dir='') 
app.add_api('openapi.yml', strict_validation=True, validate_responses=True) 
 
if __name__ == "__main__": 
    app.run(port=8080)
