from __future__ import annotations

from datetime import datetime
from operator import itemgetter
from typing import Any, Self, cast

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic_core import PydanticUndefined

from durak.shared.utils.date_time import utcnow
from durak.shared.utils.decorators import classproperty
from durak.shared.utils.types import Id


class DomainObject(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        ignored_types=(classproperty,),
        validate_assignment=True,
        validate_default=True,
    )

    def __eq__(self, other: Any) -> bool:
        # Override the `__eq__` method because the native one is also used to compare
        # private and extra attributes. We don’t need this behavior - we need
        # something similar to dataclasses
        if self.__class__ is other.__class__:
            getter = itemgetter(*self.__class__.model_fields)
            return getter(self.__dict__) == getter(other.__dict__)
        return NotImplemented

    def asdict(
        self,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        return self.model_dump(include=include, exclude=exclude)

    def replace(self: Self, **kwargs: Any) -> Self:
        return self.model_copy(update=kwargs)


class ValueObject(DomainObject):
    """A Value Object is an immutable object that represents a specific value
    with no identity.
    """

    model_config = ConfigDict(frozen=True)


class DataObject(DomainObject):
    """A Data Object is a mutable object that contains data and has no identity."""


class Entity(DomainObject):
    """An Entity is an object that have a distinct identity that runs through time and
    different representations. Such objects are important for application users.

    It's also called "reference object".
    """

    id_: Id = Id.field()


class _DiscriminatedObject(ValueObject):
    type_: str

    @property
    def entity_id(self) -> str:
        raise NotImplementedError

    @classproperty
    def type(cls) -> str:
        default = cls.model_fields['type_'].default
        type_ = cast(type, cls)
        assert default is not PydanticUndefined, f'{type_.__name__}.type_ is undefined'
        return default


class DomainEvent(_DiscriminatedObject):
    entity_name: str
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def get_subclasses(cls) -> tuple[type[DomainEvent], ...]:
        return tuple(cls.__subclasses__())

    @classproperty
    def entity(cls) -> str:
        entity = cls.model_fields['entity_name'].default
        type_ = cast(type, cls)
        assert entity is not PydanticUndefined, f'{type_.__name__}.entity is undefined'
        return entity


class Aggregate[T: DomainEvent](Entity):
    """An Aggregate is a cluster of domain objects (entities and value objects)
    that can be treated as a single unit.

    Aggregates are the basic element of transfer of data storage - you request to
    load or save whole aggregates. Transactions shouldn't cross aggregate boundaries.
    """

    events: list[T]
    _pending_event: T | None = PrivateAttr(default=None)

    def trigger_event(self, event_type: type[T], **kwargs: Any) -> None:
        kwargs[f'{event_type.entity}_id'] = self.id_
        event = event_type(**kwargs)
        self.events.append(event)
        self._pending_event = event

    def collect_last_event(self) -> T | None:
        event = self._pending_event
        self._pending_event = None
        return event

    @property
    def last_event(self) -> T:
        return self.events[-1]
