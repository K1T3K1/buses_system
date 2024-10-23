from aiohttp.web import run_app
import logging
from rich.logging import RichHandler
from rich.console import Console
from .kafka import receiver_config


handler = RichHandler(console=Console(soft_wrap=True))
logging.basicConfig(
    handlers=[handler], format="%(levelname) -2s %(asctime)s %(name) -2s %(funcName) -2s %(lineno)d:\n %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)

def main():
    logger.critical("ENTERING MAIN")
    base = receiver_config.BaseShovel()
    app = base.app

    logger.critical("about to run app")
    run_app(app, port=2137)

main()