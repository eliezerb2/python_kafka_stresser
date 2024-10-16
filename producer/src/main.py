"""
Kafka Producer Script

This script reads a single message from a JSON file, recreates a Kafka topic,
and sends multiple copies to the Kafka broker.
"""

import logging
import json
import os
from typing import Dict, Any, Optional
import random
from kafka import KafkaProducer
from utils.src.config import Config
from utils.src.logger import setup_logging


def create_producer(
    broker: str,
    batch_bytes: int,
    linger_ms: int
) -> KafkaProducer:
    """Creates a Kafka producer."""
    logging.info('Creating Kafka producer in broker: "%s"', broker)
    try:
        producer: KafkaProducer = KafkaProducer(
            bootstrap_servers=broker,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            batch_size=batch_bytes,
            linger_ms=linger_ms
        )
        logging.info('Kafka producer created: "%s"', producer.__dict__)
        return producer
    except Exception as ex:
        logging.error("Error creating consumer: %s", ex)
        return None


def create_message(
    file_path: str,
    additional_data: Dict[str, Any]
) -> dict:
    """
    Reads a JSON object from a specified file path
    and merges it with the provided dictionary.

    Parameters:
    - file_path (str): The path to the JSON file.
    - additional_data (Dict[str, Any]):
        A dictionary containing keys and values to merge.

    Returns:
    - Dict[str, Any]: A new JSON object with the merged data.
    """
    logging.info('Reading message from "%s"', file_path)
    try:
        # Read the JSON object from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        # Merge the additional data into the JSON object
        merged_data = {**json_data, **additional_data}
        return merged_data
    except FileNotFoundError:
        logging.error('File not found "%s"', file_path)
        return {}
    except json.JSONDecodeError:
        logging.error('The file does not contain valid JSON')
        return {}


def produce_messages(
    producer: KafkaProducer,
    msg: dict,
    topic_name: str,
    count: int = 1,
    timeout: Optional[int] = 10
) -> None:
    """Sends a specified number of copies of a message to the Kafka topic."""
    for counter in range(count):
        future = producer.send(topic_name, value=msg)
        try:
            # Wait for the send to complete
            record_metadata = future.get(timeout=timeout)
            logging.info(
                'Message "%s" sent message %d to partition %d with offset %d',
                msg, counter + 1,
                record_metadata.partition,
                record_metadata.offset
            )
        except KafkaError as e:
            logging.error('Error sending message: %s', e)
    producer.flush()


def set_context(
    producer: KafkaProducer,
    topic: str,
    key_name: str
) -> int:
    """Creates and sends the context event to the context Kafka topic."""
    # Generate a random context ID
    new_context_id: int = random.randint(0, 1000)
    logging.info(
        'Producing context %d to topic: "%s"',
        new_context_id, topic)
    event_data = {
        key_name: new_context_id
    }
    # Send the context to the topic
    produce_messages(producer, event_data, topic)
    return new_context_id


if __name__ == "__main__":
    setup_logging(Config.log_level)

    # Create Kafka producer
    kafka_producer = create_producer(
        Config.Kafka.broker_uri,
        Config.Producer.batch_bytes,
        Config.Producer.linger_ms
    )

    # Produce a context event
    context_id = set_context(
        kafka_producer,
        Config.Kafka.context_topic,
        Config.Kafka.context_id_key_name
    )

    # Create the message with context to produce into the data topic
    context: Dict[str, Any] = {
        Config.Kafka.context_id_key_name: context_id
    }
    message = create_message(
        os.path.join(
            Config.utils_folder_name,
            Config.Producer.message_file_name),
        context)

    # Produce the messages to the data topic
    produce_messages(
        kafka_producer,
        message,
        Config.Kafka.topic,
        Config.Producer.message_count
    )
