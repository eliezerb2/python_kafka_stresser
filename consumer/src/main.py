"""
Kafka Consumer Script

This script consumes messages from a Kafka topic as part of a consumer group.
"""

import logging
import json
import time
from typing import Optional
from threading import Thread
from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
from utils.src.config import Config
from utils.src.logger import setup_logging


def create_consumer(
    broker_uri: str,
    topic_name: str,
    group_id: Optional[str] = None,
    auto_offset_reset: Optional[str] = 'earliest',
    enable_auto_commit: Optional[bool] = True
) -> KafkaConsumer:
    """Creates a Kafka consumer."""
    logging.info(
        'Creating Kafka consumer in broker "%s", '
        'for topic "%s", with group "%s", reading "%s" with auto_commit=%s',
        broker_uri, topic_name, group_id,
        auto_offset_reset, enable_auto_commit
    )
    try:
        consumer: KafkaConsumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=broker_uri,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit
        )
        logging.info('Kafka consumer created: "%s"', consumer.__dict__)
        return consumer
    except Exception as ex:
        logging.error("Error creating consumer: %s", ex)
        return None


def check_and_reset_offset(consumer: KafkaConsumer, topic_name: str):
    """
    Check if the fetched offsets are out of range and reset them if necessary.

    Args:
        consumer (KafkaConsumer): The Kafka consumer instance.
        topic_name (str): The Kafka topic name.

    Returns:
        None
    """
    # TODO: will the consumer be assigned to partitions
    partitions = consumer.partitions_for_topic(topic_name)
    if partitions:
        # Create TopicPartition objects for each partition
        topic_partitions = [TopicPartition(topic_name, partition)
                            for partition in partitions]

        # Get the earliest and latest offsets
        earliest_offsets = consumer.beginning_offsets(topic_partitions)
        latest_offsets = consumer.end_offsets(topic_partitions)

        # Check the current offsets for each partition
        for topic_partition in topic_partitions:
            current_offset = consumer.position(topic_partition)
            earliest = earliest_offsets[topic_partition]
            latest = latest_offsets[topic_partition]

            logging.info(
                'Topic/partition %s/%d offsets: earliest=%d, current=%d, latest=%d',
                topic_name, topic_partition.partition,
                earliest, current_offset, latest)

            # Check if the current offset is out of range
            if current_offset < earliest or current_offset > latest:
                logging.warning(
                    'Resetting offset for partition %d to earliest',
                    topic_partition)
                consumer.seek_to_beginning(topic_partition)


def consume_data_messages(
    broker_uri: str,
    topic_name: str,
    group_id: str,
    context_id_key_name: str,
    context: list
) -> None:
    """
    Continuously consumes messages from the Kafka topic

    Args:
        broker_uri (str): Kafka bootstrap server.
        topic_name (str): The name of the Kafka topic to consume from.
        group_id (str): The kafka consumer group id for offset management.
        context (list):
            A mutable container to store the last consumed context messages.

    Returns:
        None
    """

    # Create a Kafka consumer for the topic
    data_consumer = create_consumer(broker_uri, topic_name, group_id)

    logging.info('Consuming messages from topic "%s"', topic_name)
    try:
        while True:
            try:
                for message in data_consumer:
                    # check_and_reset_offset(data_consumer, topic_name)
                    # Process the message
                    logging.info(
                        'Message in topic/partition/offset %s/%d/%d: "%s"',
                        topic_name, message.partition,
                        message.offset, message.value
                    )
                    # Check the context
                    if (context[0] is not None
                        and message.value[context_id_key_name]
                            == context[0].value[context_id_key_name]):
                        logging.info(
                            'Message in context from "%s"-%d-%d',
                            topic_name, message.partition, message.offset)
# TODO: can we catch kafka errors?
            # except KafkaError as ex:
            #     logging.error('KafkaError encountered: %s', ex)
            #     data_consumer.close()
            #     while data_consumer is None:
            #         data_consumer = create_consumer(
            #             broker_uri, topic_name, group_id)
            except Exception as ex:
                logging.error('Unexpected error encountered: %s', ex)
                break
    except KeyboardInterrupt:
        logging.info(
            'Consumer interrupted while reading topic "%s"',
            topic_name)
    finally:
        # Clean up by closing the consumer properly
        logging.info(
            'Closing the consumer of topic "%s"',
            topic_name)
        data_consumer.close()


def consume_last_message(
    broker_uri: str,
    topic_name: str,
    last_messages: list,
    partition: int = 0
) -> None:
    """
    Consumes the last message from a specified partition of a Kafka topic
    and continues to listen for new messages.

    Args:
        broker_uri (str): Kafka bootstrap server.
        topic_name (str): The name of the Kafka topic to consume from.
        last_messages (list):
            A mutable container to store the last consumed messages.
        partition (int): The partition number to consume from.

    Returns:
        None
    """

    kafka_consumer = create_consumer(
        broker_uri=broker_uri,
        topic_name=topic_name,
        auto_offset_reset='latest',
        enable_auto_commit=False
    )

    # Use the requested partition
    topic_partition = TopicPartition(topic_name, partition)

    # Get the last offset of the partition
    end_offsets = kafka_consumer.end_offsets([topic_partition])
    # Check if there are any messages
    last_offset: int = end_offsets[topic_partition] - 1
    if last_offset > -1:
        # Move to the last message
        logging.info(
            'Moving in topic "%s" to message at offset %d',
            topic_name, last_offset)
        kafka_consumer.seek(topic_partition, last_offset)
    else:
        logging.info('No messages in topic "%s"', topic_name)

    # Consume the last message and continue listening for new messages
    logging.info(
        'Listening for messages in topic "%s", from offset %d',
        topic_name, last_offset)
    try:
        for message in kafka_consumer:
            # Update the last message in the mutable container
            last_messages[0] = message
            logging.info(
                'From topic "%s", consumed: "%s"',
                topic_name, message)
    except KeyboardInterrupt:
        logging.info(
            'Consumer interrupted while reading topic "%s"',
            topic_name)
    finally:
        # Clean up by closing the consumer properly
        logging.info(
            'Closing the consumer of topic "%s"',
            topic_name)
        kafka_consumer.close()


if __name__ == "__main__":
    setup_logging(Config.log_level)

    # Use a list to allow updates from the context-consumer thread
    context_messages = [None]

    # Start the context consumer thread
    context_thread = Thread(
        target=consume_last_message,
        args=(
            Config.Kafka.broker,
            Config.Kafka.context_topic,
            context_messages
        )
    )
    context_thread.start()

    # Loop until a context is received
    logging.info('Waiting for context')
    while context_messages[0] is None:
        time.sleep(1)  # Sleep to avoid busy waiting
    logging.info('Received context message: "%s"', context_messages[0])

    # Continuously consume from the data topic
    consume_data_messages(
        Config.Kafka.broker_uri,
        Config.Kafka.topic,
        Config.Consumer.group_id,
        Config.Kafka.context_id_key_name,
        context_messages
    )
