from datetime import datetime, timezone
from aiohttp import web
from aiohttp.web import Request, Response
from prometheus_client import (
    CollectorRegistry,
    generate_latest,
)
import logging
from aiohttp.web import Application

logger = logging.getLogger(__name__)


class MonitoredService:
    app: Application
    registry: CollectorRegistry

    def __init__(self):
        self.app = Application()
        prometheus_monitor = PrometheusMonitor()
        prometheus_monitor.register(self)


class PrometheusMonitor:
    _latest_pull: float
    _warning_time: float = 180
    version: str = "1.0.0"

    def __init__(self) -> None:
        self._latest_pull = datetime.now(timezone.utc).timestamp()

    def __repr__(self) -> str:
        return "PrometheusMonitor"

    async def is_available(self) -> bool:
        if (self._latest_pull - datetime.now(timezone.utc).timestamp()) > self._warning_time:
            return False
        else:
            return True

    async def try_restore_health(self) -> bool:
        """
        Always returns `True` since `Prometheus` operates on Pull model
        """
        return True

    def description(self) -> dict:
        return {
            "Name": repr(self),
            "Version": self.version,
            "Description": "Resource responsible for generating metrics and monitoring communication with Prometheus",
            "Latest pull": datetime.fromtimestamp(self._latest_pull, tz=timezone.utc).isoformat(),
        }

    async def description_endpoint(self, _request: Request) -> Response:
        return Response(text=str(self.description()))

    async def handle_metrics(self, request: Request) -> Response:
        latest_metrics = generate_latest(request.app["registry"])
        self._latest_pull = datetime.now(timezone.utc).timestamp()
        return Response(text=latest_metrics.decode())

    def register(self, base_service: MonitoredService) -> None:
        metrics_endpoint = "/metrics"
        base_service.app.add_routes([web.get(metrics_endpoint, self.handle_metrics)])
        base_service.registry = CollectorRegistry()
        base_service.app["registry"] = base_service.registry
        logger.info(f"Added endpoint for {repr(self)} under {metrics_endpoint} path")
        service_endpoint = "/resources/prometheus"
        base_service.app.add_routes([web.get(service_endpoint, self.description_endpoint)])
        logger.info(f"Added endpoint for {repr(self)} under {service_endpoint} path")
