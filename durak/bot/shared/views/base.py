from abc import ABC, abstractmethod


class View(ABC):
    @abstractmethod
    async def send(self):
        raise NotImplementedError
