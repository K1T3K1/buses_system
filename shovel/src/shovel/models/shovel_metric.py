from prometheus_client import CollectorRegistry, Enum, Counter


class ShovelMetric:
    def __init__(self, registry: CollectorRegistry):
        self.registry = registry

        self.kafka_connection_state = Enum(
            "kafka_connection_state",
            "State of the Kafka connection",
            (),
            "etl",
            "shovel",
            "",
            self.registry,
            states=["connected", "disconnected"],
        )

        self.kafka_consumes = Counter(
            "shovel_kafka_consumes",
            "Number of times the shovel has consumed message from Kafka",
            ["topic"],
            "etl",
            "shovel",
            "messages",
            self.registry,
        )

        self.database_insert_tries = Counter(
            "shovel_database_insert_tries",
            "Number of times the shovel has tried to insert into database",
            ["table"],
            "etl",
            "shovel",
            "records",
            self.registry,
        )

        self.database_insert_successes = Counter(
            "shovel_database_insert_successes",
            "Number of times the shovel has succeded to insert into database",
            ["table"],
            "etl",
            "shovel",
            "records",
            self.registry,
        )

        self.errors = Counter(
            "shovel_errors",
            "Number of general errors encountered during shovel's work",
            ["reason"],
            "etl",
            "shovel",
            "errors",
            self.registry,
        )
