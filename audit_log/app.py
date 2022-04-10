import connexion
import yaml
import logging
import logging.config
import json
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
import connexion
from connexion import NoContent

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

def get_artist_reading(index):
    """ Get artist Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving artist reading at index %d" % index)
    counter = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'artists':
                if counter == index:
                    return payload, 200
                counter += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find artist reading at index %d" % index)
    return {"message": "Not Found"}, 404

def get_song_reading(index):
    """ Get song Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving song reading at index %d" % index)
    counter = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'songs':
                if counter == index:
                    return payload, 200
                counter += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find song reading at index %d" % index)
    return {"message": "Not Found"}, 404

def health():
    logger.info('Audit service is running')
    return NoContent, 200

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8110)
