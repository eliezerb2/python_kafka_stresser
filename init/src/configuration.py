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
    consumer_instance_count: int = \
        int(os.environ.get("CONSUMER_INSTANCE_COUNT", 1))
    kafka_broker_uri: str = \
        kafka_broker + ":" + kafka_broker_internal_port
