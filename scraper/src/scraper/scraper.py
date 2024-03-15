import aiohttp as aio
import pyarrow.parquet as pq
import asyncio
import logging
from .models.parquet_model import ParquetModel
from .models.scraper_metric import ScraperMetric
from .kafka.topic import Topic
import io
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
        type: type[ParquetModel],
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
            parquet = model.to_parquet()
            pbytes = io.BytesIO()
            pq.write_table(parquet, pbytes)

            self._metric.kafka_publish_tries.labels(self._topic._name).inc()
            await self._topic.publish(pbytes.getvalue())
            self._metric.kafka_publish.labels(self._topic._name).inc()

            if self._helper_topic:
                json = model.model_dump_json()
                self._metric.kafka_publish_tries.labels(self._helper_topic._name).inc()
                await self._helper_topic.publish(json.encode())
                self._metric.kafka_publish.labels(self._helper_topic._name).inc()
            logger.critical(f"Data from {self._path} published to Kafka")
