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
    kafka_group_id: str = \
        os.environ.get('KAFKA_GROUP_ID', 'test_group')
    kafka_broker_uri: str = \
        kafka_broker + ":" + kafka_broker_internal_port
