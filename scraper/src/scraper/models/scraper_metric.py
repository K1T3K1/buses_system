from prometheus_client import CollectorRegistry, Counter, Enum

class ScraperMetric:
    def __init__(self, registry: CollectorRegistry):
        self.registry = registry

        self.times_scraped = Counter(
            "scraper_times_scraped",
            "Number of times the scraper has scraped data",
            ["scraped_type"],
            'etl',
            'scraper',
            'tries',
            self.registry
        )

        self.kafka_publish = Counter(
            "scraper_kafka_publish",
            "Number of times the scraper has published to Kafka",
            ["topic"],
            'etl',
            'scraper',
            'messages',
            self.registry
        )

        self.kafka_publish_tries = Counter(
            "scraper_kafka_publish_tries",
            "Number of times the scraper has tried to publish to Kafka",
            ["topic"],
            'etl',
            'scraper',
            'tries',
            self.registry
        )

        self.kafka_connection_state = Enum(
            "kafka_connection_state",
            "State of the Kafka connection",
            (),
            'etl',
            'scraper',
            '',
            self.registry,
            states=["connected", "disconnected"]
        )