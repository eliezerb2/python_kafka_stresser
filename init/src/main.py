"""
Manager Script

This script will init the Kafka topic
"""

import logging
from configuration import Config
from kafka import KafkaAdminClient
from kafka.admin import NewTopic


def setup_logging():
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def create_admin_client(broker: str) -> KafkaAdminClient:
    """Creates a Kafka admin client."""
    return KafkaAdminClient(bootstrap_servers=broker)


def create_topic(admin_client: KafkaAdminClient,
                 topic_name: str,
                 num_partitions: int) -> None:
    """creates a Kafka topic."""

    # Check if the topic exists
    replication_factor = 1
    existing_topics = admin_client.list_topics()

    if topic_name in existing_topics:
        logging.info('Topic "%s" already exists.', topic_name)
    else:
        # Create the topic
        try:
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor)
            admin_client.create_topics(
                [new_topic],
                validate_only=False
            )
            logging.info("Topic '%s' created with %d partitions\
                         and replication factor %d.",
                         topic_name, num_partitions, replication_factor)

        except Exception as ex:
            logging.error("Error creating topic '%s': %s", topic_name, ex)


if __name__ == "__main__":
    setup_logging()

    # Create Kafka admin client to manage topics
    kafka_admin_client = create_admin_client(Config.kafka_broker_uri)

    # Create the Kafka topic
    create_topic(kafka_admin_client,
                 Config.kafka_topic,
                 Config.consumer_instance_count)
