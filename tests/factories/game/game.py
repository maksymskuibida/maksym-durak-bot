import factory

from durak.game.domain.model.game import Game
from tests.factories.base import Factory
from tests.factories.game.player import PlayerFactory


class GameFactory(Factory[Game]):
    class Meta:
        model = Game

    players = factory.List(
        [
            factory.SubFactory(PlayerFactory),
            factory.SubFactory(PlayerFactory),
        ]
    )
