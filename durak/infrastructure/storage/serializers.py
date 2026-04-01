from typing import Protocol, TypeVar

from bson import ObjectId

from durak.infrastructure.storage.protocols import PEntitySerializer


class SupportsAsDict(Protocol):
    def asdict(self) -> dict: ...


T = TypeVar('T', bound=SupportsAsDict)


class AggregateSerializer(PEntitySerializer[T, dict]):
    def __init__(self, model_cls: type[T]):
        self.model_cls = model_cls

    def to_representation(self, entity: T) -> dict:
        return entity.asdict()

    def to_internal_value(self, payload: dict) -> T:
        return self.model_cls(**payload)


class MongoSerializer(AggregateSerializer[T]):
    def to_representation(self, entity: T) -> dict:
        value = super().to_representation(entity)
        _id = value.pop('id_', None)
        if _id:
            value['_id'] = ObjectId(_id)
        return value

    def to_internal_value(self, payload: dict) -> T:
        payload['id_'] = str(payload.pop('_id'))
        return super().to_internal_value(payload)
