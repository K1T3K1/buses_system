from aiokafka import AIOKafkaConsumer, ConsumerRecord
import asyncio
import avro
from avro.io import BinaryDecoder, DatumReader
import io
from ..shovel import upload_row
import logging
from libraries.pg_models.positions import Position
from asyncio import Semaphore
from ..models.shovel_metric import ShovelMetric
from functools import partial

logger = logging.getLogger(__name__)

tasks = set()

_running_vehicles_schema = avro.schema.parse(open("../avro/vehicle.avsc").read())


async def running_vehicles_generator(row, metric: ShovelMetric):
    row = Position(
        line_name=int(row["line_name"]),
        course_loid=row["course_loid"],
        day_course_loid=row["day_course_loid"],
        vehicle_id=row["vehicle_id"],
        delay_sec=row["delay_sec"],
        longitude=row["longitude"],
        latitude=row["latitude"],
        angle=row["angle"],
        reached_meters=row["reached_meters"],
        variant_loid=row["variant_loid"],
        last_ping_date=row["last_ping_date"],
        distance_to_nearest_stop_point=row["distance_to_nearest_stop_point"],
        nearest_symbol=row["nearest_symbol"],
        operator=row["operator"],
        on_stop_point=row["on_stop_point"],
        order_in_course=row["order_in_course"],
        optional_direction=row["optional_direction"],
    )

    await upload_row(row, metric)

def callback(task, semaphore: Semaphore):
    tasks.discard(task)
    semaphore.release()

async def message_loop(kafka: AIOKafkaConsumer, metric: ShovelMetric) -> None:
    sem = Semaphore(4)
    loop = asyncio.get_running_loop()
    logger.critical("Starting message loop")
    while True:
        await sem.acquire()
        msg = await kafka.getone()
        metric.kafka_consumes.labels("running_vehicles").inc()
        t = loop.create_task(handle_message(msg, sem, metric))
        tasks.add(t)
        t.add_done_callback(lambda task: callback(task, sem))


async def handle_message(msg: ConsumerRecord, sem: Semaphore, metric: ShovelMetric):
    reader = DatumReader(writers_schema=_running_vehicles_schema)
    buffer = io.BytesIO(msg.value)
    decoder = BinaryDecoder(buffer)
    row = reader.read(decoder)
    await running_vehicles_generator(row, metric)

