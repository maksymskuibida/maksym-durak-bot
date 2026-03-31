import pytest

from durak.game.domain.exceptions import DefenderHasNotBeenPickedError
from tests.factories.game.game import GameFactory


def test_defender_raises_if_defender_has_not_been_picked_yet():
    game = GameFactory.build()

    with pytest.raises(DefenderHasNotBeenPickedError) as exc_info:
        _ = game.defender

    assert exc_info.value.message == 'Defender has not been picked yet'
