from pydantic import BaseModel, ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel
from typing import Optional

class LineValidity(BaseModel):
    _from: int = Field(validation_alias="from", serialization_alias="from")
    until: int

class Departure(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel, serialization_alias=to_camel)
    )
    scheduled_departer_sec: int
    brigade: str
    course_id: int
    variant_id: int
    operator: Optional[str] = None
    transport_type: str
    expected_vehicle_type: str
    order_in_course: int
    optional_direction: str
    letter: str
    visible: bool
    workaround_id: Optional[int]
    overloaded_id: Optional[int]
    coursenstart_sec: int
    multiple_legends: list
    
class LineSchedule(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel, serialization_alias=to_camel)
    )
    line_name: str
    is_getting_out_only: bool
    destination: str
    main_variant_id: int
    override_letters: dict[str, str]
    departures: list[Departure]
    line_validity: LineValidity

class AtomicSchedule(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel, serialization_alias=to_camel)
    )
    day_type_symbol: str
    getting_out_variants: list
    line_schedules: dict[str, LineSchedule]
