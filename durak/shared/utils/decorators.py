from typing import Any, Callable


class classproperty:
    """Decorator that implements a read-only managed attribute at the class level.

    Attempting to access a classproperty from an instance raises an AttributeError.
    """

    def __init__(self, method: Callable[[Any], Any]) -> None:
        self.fget = method

    def __get__(self, instance: object | None = None, owner: type | None = None) -> Any:
        if instance is None:
            return self.fget(owner)
        _name = self.__class__.__name__
        raise AttributeError(f'Cannot access {_name} on an instance of {owner}.')
