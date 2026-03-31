import pytest

from tests.factories.game.player import PlayerFactory


@pytest.fixture
def get_players():
    def _get_players(n: int):
        return [PlayerFactory.build() for _ in range(n)]

    return _get_players
