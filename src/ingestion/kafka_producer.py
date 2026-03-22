import json
import time
from datetime import datetime
from kafka import KafkaProducer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RealKafkaProducer:
    def __init__(self, bootstrap_servers="kafka:29092"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=self._json_serializer).encode('utf-8')
        )
        logger.info(f"Kafka producer connected to {bootstrap_servers}")

    def _json_serializer(self, obj):
        """Преобразует объекты, которые не могут быть сериализованы в JSON"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'item'):
            return obj.item()
        raise TypeError(f"Type {type(obj)} not serializable")

    def send_transaction(self, topic, transaction):
        future = self.producer.send(topic, value=transaction)
        result = future.get(timeout=10)
        logger.debug(f"Sent to {topic}: partition={result.partition}, offset={result.offset}")
        return result

    def close(self):
        self.producer.close()