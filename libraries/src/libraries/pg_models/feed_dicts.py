from aiokafka import AIOKafkaConsumer
import io
from avro.io import DatumReader, BinaryDecoder
import avro
from operators import Operator
from directions import Direction
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
import asyncio

engine = create_async_engine('postgresql+asyncpg://admin:admin@localhost:5432/buses')
print("Created engine")
_schema = avro.schema.parse(open("../../../../avro/vehicle.avsc").read())
print("read schema")

tasks = set()

directions = {}
operators = {}

class Counter:
    value: int

    def __init__(self):
        self.value = 0

async def prefeed():
    async with AsyncSession(engine) as conn:
        stmtdir = select(Direction)
        direcs = (await conn.execute(stmtdir)).all()
        stmtoper = select(Operator)
        opers = (await conn.execute(stmtoper)).all()
        for d in direcs:
            directions[d.Direction.value] = True
        for o in opers:
            operators[o.Operator.value] = True

async def consume():
    await prefeed()
    counter = Counter()

    consumer = AIOKafkaConsumer(
        'running_vehicles',
        bootstrap_servers='localhost:29092',
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )
    print("Created consumer")
    consumer.subscribe(['running_vehicles'])
    print("Subscribed")
    
    await consumer.start()
    print("Started")
    await consumer.seek_to_beginning()
    print("seeked")
    try:
        loop = asyncio.get_running_loop()
        async for msg in consumer:
            t = loop.create_task(message(msg, counter))
            tasks.add(t)
            t.add_done_callback(tasks.discard)


    except Exception as e:
        print(e)

async def message(msg, counter):
    print(counter.value)
    reader = DatumReader(_schema)
    buffer = io.BytesIO(msg.value)
    decoder = BinaryDecoder(buffer)
    vehicle = reader.read(decoder)

    direction = Direction(
        value=vehicle["optional_direction"]
    )
    
    async with AsyncSession(engine) as conn:
        if not directions.get(direction.value, False):
            try:
                conn.add(direction)
                await conn.commit()
            except Exception as e:
                await conn.rollback()
        
        operator = Operator(
            value=vehicle["operator"]
        )
        if not operators.get(operator.value, False):
            try:
                conn.add(operator)
                await conn.commit()
            except Exception as e:
                await conn.rollback()
        counter.value += 1

asyncio.run(consume())


