"""
Load configurations from environment variables
"""

import os


class Config:
    """
    The main configuration
    """

    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    utils_folder_name: str = os.environ.get("UTILS_FOLDER_NAME", "utils")

    class Kafka:
        """
        General Kafka configuration
        """
        broker_internal_port: str = \
            os.environ.get("KAFKA_BROKER_INTERNAL_PORT", "9092")
        broker: str = \
            os.environ.get("KAFKA_CONTAINER_NAME", "kafka")
        topic: str = \
            os.environ.get('KAFKA_TOPIC', 'test_topic')
        broker_uri: str = \
            broker + ":" + broker_internal_port
        context_topic: str = \
            os.environ.get('KAFKA_CONTEXT_TOPIC', "context_topic")
        context_id_key_name: str = \
            os.environ.get('CONTEXT_ID_KEY_NAME', "context_id")

    class Producer:
        """
        Producer specific configuration
        """
        message_count: int = \
            int(os.environ.get("MESSAGE_COUNT", 10))
        message_file_name: str = \
            os.environ.get("MESSAGE_FILE_NAME", "message.json")
        batch_bytes: int = \
            int(os.environ.get("BATCH_BYTES", 1024))
        linger_ms: int = \
            int(os.environ.get("LINGER_MS", 1))

    class Consumer:
        """
        Specific consumer configuration
        """
        instance_count: int = \
            int(os.environ.get("CONSUMER_INSTANCE_COUNT", 1))
        group_id: str = \
            os.environ.get('KAFKA_GROUP_ID', 'test_group')
