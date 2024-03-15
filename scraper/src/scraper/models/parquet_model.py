from pydantic import BaseModel
import pyarrow as pa
from abc import ABC, abstractmethod

class ParquetModel(BaseModel, ABC):
    @abstractmethod
    def to_parquet(self) -> pa.Table:
        pass