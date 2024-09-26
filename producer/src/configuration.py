"""
Load configurations from environment variables
"""

import os


class Config:
    """
    The main configuration
    """
    kafka_broker_internal_port: str = \
        os.environ.get("KAFKA_BROKER_INTERNAL_PORT", "9092")
    kafka_broker: str = \
        os.environ.get("KAFKA_CONTAINER_NAME", "kafka")
    kafka_topic: str = \
        os.environ.get('KAFKA_TOPIC', 'test_topic')
    kafka_broker_uri: str = \
        kafka_broker + ":" + kafka_broker_internal_port
    message_count: int = \
        int(os.environ.get("MESSAGE_COUNT", 10))
    message_file_path: str = \
        os.environ.get("MESSAGE_FILE_PATH", "message.json")
    consumer_instance_count: int = \
        int(os.environ.get("CONSUMER_INSTANCE_COUNT", 1))
    batch_bytes: int = \
        int(os.environ.get("BATCH_BYTES", 1024))
    linger_ms: int = \
        int(os.environ.get("LINGER_MS", 1))
