from aiokafka import AIOKafkaProducer

class Topic:
    def __init__(self, name: str, producer: AIOKafkaProducer) -> None:
        self._name = name
        self._producer = producer

    async def publish(self, data: bytes) -> None:
        await self._producer.send_and_wait(self._name, data)