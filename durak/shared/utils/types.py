from typing import Any, Self

import nanoid
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class Id(str):
    @classmethod
    def create(cls) -> Self:
        return cls(nanoid.generate())

    @classmethod
    def field(cls) -> Self:
        return Field(default_factory=cls.create)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))
