from aiohttp.web import run_app, Application
import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from .kafka.producer_config import kafka_context
from rich.logging import RichHandler
from rich.console import Console
from .kafka import producer_config

handler = RichHandler(console=Console(soft_wrap=True))
logging.basicConfig(
    handlers=[handler],
    format="%(levelname) -2s %(asctime)s %(name) -2s %(funcName) -2s %(lineno)d:\n %(message)s"
)


def main():
    base = producer_config.BaseScraper()
    app = base.app

    run_app(app, port=1337)

