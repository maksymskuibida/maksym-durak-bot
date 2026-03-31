import pytest

from durak.game.domain.exceptions import (
    GameIsAlreadyFinishedError,
    GameIsAlreadyInProgressError,
    PlayerIsAlreadyInTheGameError,
    PlayersCountExceedMaxPlayersCountError,
)
from durak.game.domain.model.game import GameStatus, MAX_PLAYERS
from tests.factories.game.game import GameFactory
from tests.factories.game.player import PlayerFactory


def test_add_player_happy_path():
    game = GameFactory.build()
    player = PlayerFactory.build()

    players_count_before = len(game.players)
    game.add_player(player)

    assert player in game.players
    assert len(game.players) == players_count_before + 1


@pytest.mark.parametrize(
    ('game_status', 'expected_error', 'expected_message'),
    (
        (
            GameStatus.IN_PROGRESS,
            GameIsAlreadyInProgressError,
            'Game is already in progress',
        ),
        (GameStatus.FINISHED, GameIsAlreadyFinishedError, 'Game is already finished'),
    ),
)
def test_add_player_raises_if_game_is_not_pending(
    game_status, expected_error, expected_message
):
    game = GameFactory.build(status=game_status)

    with pytest.raises(expected_error) as exc_info:
        game.add_player(PlayerFactory.build())
    assert exc_info.value.message == expected_message


def test_add_player_raises_if_player_already_in_game():
    game = GameFactory.build()

    with pytest.raises(PlayerIsAlreadyInTheGameError) as exc_info:
        game.add_player(game.players[0])

    assert (
        exc_info.value.message == 'Player %s is already in the game' % game.players[0]
    )


def test_add_player_raises_if_players_count_exceed_max_players_count():
    game = GameFactory.build(
        players=[PlayerFactory.build() for _ in range(MAX_PLAYERS)]
    )

    with pytest.raises(PlayersCountExceedMaxPlayersCountError) as exc_info:
        game.add_player(PlayerFactory.build())

    assert exc_info.value.message == 'Players count exceed max players count %s' % str(
        MAX_PLAYERS
    )
