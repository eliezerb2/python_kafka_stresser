"""
Kafka Consumer Script

This script consumes messages from a Kafka topic as part of a consumer group.
"""

import logging
import json
from configuration import Config
from kafka import KafkaConsumer


def setup_logging():
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )


def create_consumer(broker: str, topic: str, group_id: str) -> KafkaConsumer:
    """Creates a Kafka consumer."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=broker,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )


def consume_messages(consumer: KafkaConsumer) -> None:
    """Continuously consumes messages from the Kafka topic."""
    logging.info("Starting to consume messages...")

    try:
        for message in consumer:
            # Process the message
            logging.info("Received message: %s from partition %s at offset %s",
                         message.value, message.partition, message.offset)
    except KeyboardInterrupt:
        print("Consumer interrupted")
    finally:
        # Clean up by closing the consumer properly
        consumer.close()


if __name__ == "__main__":
    setup_logging()

    # Create Kafka consumer
    kafka_consumer = create_consumer(Config.kafka_broker_uri,
                                     Config.kafka_topic,
                                     Config.kafka_group_id)

    # Start consuming messages
    consume_messages(kafka_consumer)
