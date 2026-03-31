from inspect import isclass
from typing import Any

import factory
from factory.declarations import BaseDeclaration
from pydantic import BaseModel


def _is_allowed_field(model_cls: type, field: str, value: Any) -> bool:
    if issubclass(model_cls, BaseModel):
        return field in model_cls.model_fields
    if isclass(model_cls) and issubclass(model_cls, factory.Factory):
        return False
    return True


class Factory[T](factory.Factory[T]):
    _factories: list[type[factory.Factory]] = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls._factories.append(cls)

    @classmethod
    def _reset_all_sequences(cls) -> None:
        for factory_cls in cls._factories:
            factory_cls.reset_sequence(force=True)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Filter out declarations of nested factories. We don't want to pass them
        # to the model constructor.
        new_kwargs = {
            key: value
            for key, value in kwargs.items()
            if _is_allowed_field(model_class, key, value)
        }
        return super()._create(model_class, *args, **new_kwargs)


class NamedSequence(BaseDeclaration):
    def __init__(self, prefix, suffix=''):
        super().__init__()
        self.prefix = prefix
        self.suffix = suffix

    def evaluate(self, instance, step, extra):
        return f'{self.prefix} #{step.sequence}'


class IDSequence(NamedSequence):
    def evaluate(self, instance, step, extra):
        return f'{self.prefix}-{step.sequence}' + (self.suffix and f'-{self.suffix}')
