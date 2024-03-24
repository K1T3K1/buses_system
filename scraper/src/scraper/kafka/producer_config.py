from aiohttp.web import Application
from aiokafka import AIOKafkaProducer
from .topic import Topic
import os
import json
from ..scraper import Scraper
from ..models.running_vehicles import RunningVehicles
import logging
from prometheus_client import CollectorRegistry, Counter, Enum
from libraries.monitored_service import MonitoredService
import asyncio
from ..models.scraper_metric import ScraperMetric
from functools import partial

logger = logging.getLogger(__name__)

class BaseScraper(MonitoredService):
    def __init__(self):
        super().__init__()
        pkafka_context = partial(kafka_context, registry=self.registry)
        self.app.cleanup_ctx.append(pkafka_context)

async def kafka_context(app: Application, registry: CollectorRegistry):
    await asyncio.sleep(10)
    metric = ScraperMetric(registry)
    kafka_server = os.getenv("KAFKA_SERVER", "kafka:29092")
    topics = json.loads(os.getenv("TOPICS", '["running_vehicles", "running_vehicles_json"]'))
    kafka = AIOKafkaProducer(
        bootstrap_servers=kafka_server,
    )
    await kafka.start()
    kafka_connection_task = asyncio.create_task(kafka_connection(kafka, metric))

    for topic in topics:
        app[topic] = Topic(topic, kafka)

    # ADD SCRAPERS HERE
    
    
    
    scraper = Scraper(
        "https://przystanki.bialystok.pl",
        30,
        "/portal/getRunningVehicles.json",
        app["running_vehicles"],
        RunningVehicles,
        metric,
        app["running_vehicles_json"],
    )
    


    # ADD SCRAPERS HERE

    logger.critical("Startup finished")

    yield

async def kafka_connection(kafka: AIOKafkaProducer, metric: ScraperMetric):
    while True:
        state = await kafka.client.ready()
        if state:
            metric.kafka_connection_state.state("connected")
        else:
            metric.kafka_connection_state.state("disconnected")
        await asyncio.sleep(15)