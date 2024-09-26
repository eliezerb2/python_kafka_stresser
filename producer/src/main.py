"""
Kafka Producer Script

This script reads a single message from a JSON file, recreates a Kafka topic, 
and sends multiple copies to the Kafka broker.
"""

import logging
import json
from configuration import Config
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic


def setup_logging():
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def create_producer(broker: str,
                    batch_bytes: int,
                    linger_ms: int) -> KafkaProducer:
    """Creates a Kafka producer."""
    return KafkaProducer(
        bootstrap_servers=broker,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        batch_size=batch_bytes,
        linger_ms=linger_ms
    )


def create_admin_client(broker: str) -> KafkaAdminClient:
    """Creates a Kafka admin client."""
    return KafkaAdminClient(bootstrap_servers=broker)


def read_message_from_file(file_path: str) -> dict:
    """Reads a single message from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def produce_messages(producer: KafkaProducer,
                     msg: dict,
                     count: int,
                     topic: str) -> None:
    """Sends a specified number of copies of a message to the Kafka topic."""
    for i in range(count):
        future = producer.send(topic, value=msg)
        try:
            # Wait for the send to complete
            record_metadata = future.get(timeout=10)
            logging.info('Message "%s" sent message %d\
                         to partition %d with offset %d',
                         msg, i + 1, record_metadata.partition,
                         record_metadata.offset)
        except KafkaError as e:
            logging.error('Error sending message: %s', e)
    producer.flush()


if __name__ == "__main__":
    setup_logging()

    # Create Kafka admin client to manage topics
    admin_client = create_admin_client(Config.kafka_broker_uri)

    # Create Kafka producer
    kafka_producer = create_producer(Config.kafka_broker_uri,
                                     Config.batch_bytes,
                                     Config.linger_ms)

    # Read the message from the JSON file
    message = read_message_from_file(Config.message_file_path)

    # Produce the messages
    produce_messages(kafka_producer,
                     message,
                     Config.message_count,
                     Config.kafka_topic)
