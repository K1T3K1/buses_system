import logging
from libraries.pg_models.positions import Position
from libraries.pg_models.operators import Operator
from libraries.pg_models.directions import Direction
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session
from .models.shovel_metric import ShovelMetric

logger = logging.getLogger(__name__)

directions = {}
operators = {}
def prefeed():
    engine = create_engine('postgresql+psycopg://admin:admin@postgres:5432/buses')
    with Session(engine) as conn:
        stmtdir = select(Direction)
        direcs = conn.execute(stmtdir).all()
        stmtoper = select(Operator)
        opers = conn.execute(stmtoper).all()
        for d in direcs:
            directions[d.Direction.value] = d.Direction.id
        for o in opers:
            operators[o.Operator.value] = o.Operator.id

prefeed()

async_engine = create_async_engine('postgresql+asyncpg://admin:admin@postgres:5432/buses')

async def upload_row(
    row: Position,
    metric: ShovelMetric
) -> None:
    direction_id = directions.get(row.optional_direction, False)
    operator_id = operators.get(row.operator, False)
    try:
        if not direction_id:
            async with AsyncSession(async_engine) as conn:
                direction_id = await add_direction(row, conn, metric)
    except Exception as e:
        #logger.warning(e)
        metric.errors.labels("Duplicate Direction Insert")
        async with AsyncSession(async_engine) as conn:
            direction_id = (await get_direction(conn, row)).Direction.id
            
    try:    
        if not operator_id:
            async with AsyncSession(async_engine) as conn:
                operator_id = await add_operator(row, conn, metric)
    except Exception as e:
        #logger.warning(e)
        metric.errors.labels("Duplicate Operator Insert").inc()
        async with AsyncSession(async_engine) as conn:
            operator_id = (await get_operator(conn, row)).Operator.id

    row.optional_direction = direction_id
    row.operator = operator_id
        
    metric.database_insert_tries.labels("positions").inc()
    async with AsyncSession(async_engine) as conn:
        conn.add(row)
        await conn.commit()
    metric.database_insert_successes.labels("positions").inc()

async def add_direction(row, conn, metric) -> int:
    d = Direction(value=row.optional_direction)
    metric.database_insert_tries.labels("directions").inc()
    conn.add(d)
    await conn.commit()
    metric.database_insert_successes.labels("directions").inc()
    direction_id = await get_direction(conn, row)
    directions[direction_id.Direction.value] = direction_id.Direction.id
    direction_id = directions[direction_id.Direction.value]
    return direction_id

async def get_direction(conn, row):
    stmtdir = select(Direction).where(Direction.value == row.optional_direction)
    return (await conn.execute(stmtdir)).fetchone()

async def add_operator(row, conn,metric) -> int:
    o = Operator(value=row.operator)
    metric.database_insert_tries.labels("operators").inc()
    conn.add(o)
    await conn.commit()
    metric.database_insert_successes.labels("operators").inc()
    operator_id = await get_operator(conn, row)
    operators[operator_id.Operator.value] = operator_id.Operator.id
    operator_id = operators[operator_id.Operator.value]
    return operator_id
        
async def get_operator(conn, row):
    stmtoper = select(Operator).where(Operator.value == row.operator)
    return (await conn.execute(stmtoper)).fetchone()


