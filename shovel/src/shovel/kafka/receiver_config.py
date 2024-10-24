from aiohttp.web import Application
from aiokafka import AIOKafkaConsumer
import os
import json
import logging
from prometheus_client import CollectorRegistry
from libraries.monitored_service import MonitoredService
import asyncio
from ..models.shovel_metric import ShovelMetric
from functools import partial
from .message_loop import message_loop

logger = logging.getLogger(__name__)
aiokafka_logger = logging.getLogger('aiokafka')
aiokafka_logger.setLevel(logging.WARNING)

class BaseShovel(MonitoredService):
    def __init__(self):
        super().__init__()
        pkafka_context = partial(kafka_context, registry=self.registry)
        self.app.cleanup_ctx.append(pkafka_context)

async def kafka_context(app: Application, registry: CollectorRegistry):
    await asyncio.sleep(10)
    metric = ShovelMetric(registry)
    kafka_server = os.getenv("KAFKA_SERVER", "localhost:29092")
    topics = json.loads(os.getenv("TOPICS", '["running_vehicles"]'))
    kafka = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=kafka_server,
        enable_auto_commit=True,
        group_id="vehicles_uploader",
        auto_offset_reset="earliest",
        auto_commit_interval_ms=10000,
        heartbeat_interval_ms=20000,
        request_timeout_ms=60000,
        session_timeout_ms=60000,
    )
    await kafka.start()
    kafka_connection_task = asyncio.create_task(kafka_connection(kafka, metric))


    task = asyncio.create_task(message_loop(kafka, metric))

    logger.critical("Startup finished")
    yield
    task.cancel()

async def kafka_connection(kafka: AIOKafkaConsumer, metric: ShovelMetric):
    while True:
        state = await kafka._client.ready()
        if state:
            metric.kafka_connection_state.state("connected")
        else:
            metric.kafka_connection_state.state("disconnected")
        await asyncio.sleep(15)