from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Iterator

class AvroModel(BaseModel, ABC):
    @abstractmethod
    def to_avro(self) -> bytes | Iterator[bytes]:
        pass