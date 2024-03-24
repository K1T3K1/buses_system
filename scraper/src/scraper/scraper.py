import aiohttp as aio
import asyncio
import logging
from .models.scraper_metric import ScraperMetric
from .models.avro_model import AvroModel
from .kafka.topic import Topic
from aiohttp.web import Application
from typing import Optional

logger = logging.getLogger(__name__)


class Scraper:
    _client: aio.ClientSession
    _frequency: int
    _target_dir: str
    _url: str
    _path: str
    _tasks: set[asyncio.Task]

    def __init__(
        self,
        url: str,
        frequency: int,
        path: str,
        topic: Topic,
        type: type[AvroModel],
        metric: ScraperMetric,
        helper_topic: Optional[Topic] = None,
    ) -> None:
        self._client = aio.ClientSession(url)
        self._url = url
        self._path = path
        self._frequency = frequency
        self._topic = topic
        self._type = type
        self._helper_topic = helper_topic
        self._metric = metric
        self._tasks = set()
        self._tasks.add(asyncio.create_task(self._get_data()))
        logger.critical(f"Scraper for {self._url}{self._path} initialized")

    async def context(self, app: Application) -> None:
        self._tasks.add(asyncio.create_task(self._get_data()))
        yield

    async def _get_data(self) -> None:
        while True:
            try:
                await self.get_data()
                await asyncio.sleep(self._frequency)
            except Exception as e:
                logger.critical(e)

    async def get_data(self) -> None:
        async with self._client.get(self._path) as resp:
            self._metric.times_scraped.labels(self._path).inc()
            logger.critical(f"Getting data from {self._url}{self._path}")

            response_text = await resp.text()
            model = self._type.model_validate_json(response_text)

            avro = model.to_avro()

            if isinstance(avro, bytes):
                await self.publish(avro)
            else:
                for data in avro:
                    await self.publish(data)

            logger.critical(f"Data from {self._path} published to Kafka")

    async def publish(self, data: bytes) -> None:
        self._metric.kafka_publish_tries.labels(self._topic._name).inc()
        await self._topic.publish(data)
        self._metric.kafka_publish.labels(self._topic._name).inc()


