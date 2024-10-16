"""
Manager Script

This script will init the Kafka topic
"""

import logging
from typing import Optional
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from utils.src.config import Config
from utils.src.logger import setup_logging


def create_admin_client(broker: str) -> KafkaAdminClient:
    """Creates a Kafka admin client."""
    logging.info('Creating Kafka Admin Client in: "%s"', broker)
    return KafkaAdminClient(bootstrap_servers=broker)


def create_topic(
    admin_client: KafkaAdminClient,
    topic_name: str,
    num_partitions: Optional[int] = 1,
    replication_factor: Optional[int] = 1
) -> None:
    """creates a Kafka topic."""
    logging.info(
        'Creating topic "%s", with %d partitions',
        topic_name, num_partitions)

    # Check if the topic exists
    if topic_name in admin_client.list_topics():
        try:
            # Delete the existing topic
            logging.info('Deleting existing topic "%s"', topic_name)
            admin_client.delete_topics([topic_name])
            logging.info('Topic "%s" deleted successfully', topic_name)
        except Exception as ex:
            logging.error('Error deleting topic "%s": %s', topic_name, ex)
            return  # Exit function if topic deletion fails

    # Create the topic
    try:
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        admin_client.create_topics(
            [new_topic],
            validate_only=False)
        logging.info(
            'Created "%s" with %d partitions and replication factor %d',
            topic_name, num_partitions, replication_factor)
    except Exception as ex:
        logging.error('Error creating topic "%s": %s', topic_name, ex)


if __name__ == "__main__":
    setup_logging(Config.log_level)

    # Create Kafka admin client to manage topics
    kafka_admin_client = create_admin_client(Config.Kafka.broker_uri)

    # Create the Kafka topic
    create_topic(
        kafka_admin_client,
        Config.Kafka.topic,
        Config.Consumer.instance_count
    )

    # Create the Kafka context topic
    create_topic(
        kafka_admin_client,
        Config.Kafka.context_topic)
