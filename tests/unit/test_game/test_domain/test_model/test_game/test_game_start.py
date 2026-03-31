import pytest

from durak.game.domain.constants import HAND_SIZE
from durak.game.domain.exceptions import (
    AtLeast2PlayersRequiredError,
    GameIsAlreadyFinishedError,
    GameIsAlreadyInProgressError,
    PlayersCountExceedMaxPlayersCountError,
)
from durak.game.domain.model.card import MAX_CARDS
from durak.game.domain.model.game import Game, GameStatus, MAX_PLAYERS
from tests.factories.game.game import GameFactory
from tests.factories.game.player import PlayerFactory


def test_create_game_defaults(snapshot_json):
    game = GameFactory.build()
    assert game.status == GameStatus.PENDING
    assert len(game.players) == 2
    assert game.deck.cards_count == MAX_CARDS


def test_start(get_players):
    players = get_players(3)
    game = Game(players=players)
    game.start()

    assert game.status == GameStatus.IN_PROGRESS
    assert game.trump is not None
    assert game.defender_id in [player.id_ for player in game.players]
    for player in game.players:
        assert len(player.hand) == HAND_SIZE
        # ensure no duplicate cards in a player's hand
        for i in range(len(player.hand)):
            for j in range(i + 1, len(player.hand)):
                assert player.hand[i] != player.hand[j]
    assert game.deck.cards_count == MAX_CARDS - HAND_SIZE * len(game.players)


def test_starts_with_first_player_set():
    first_defender_id = 'ID-1'

    game = GameFactory.build(first_defender_id=first_defender_id)

    game.start()
    assert game.defender_id == first_defender_id
    assert game.defender_id in [player.id_ for player in game.players]


def test_start_raises_if_already_in_progress():
    game = GameFactory.build(status=GameStatus.IN_PROGRESS)

    with pytest.raises(GameIsAlreadyInProgressError) as exc_info:
        game.start()

    assert exc_info.value.message == 'Game is already in progress'


def test_start_raises_if_game_finished():
    game = GameFactory.build(status=GameStatus.FINISHED)

    with pytest.raises(GameIsAlreadyFinishedError) as exc_info:
        game.start()

    assert exc_info.value.message == 'Game is already finished'


def test_start_raises_if_less_than_2_players():
    game = GameFactory.build(players=[PlayerFactory.build()])

    with pytest.raises(AtLeast2PlayersRequiredError) as exc_info:
        game.start()

    assert exc_info.value.message == 'At least 2 players required'


def test_start_raises_if_more_than_max_players(get_players):
    game = GameFactory.build(players=get_players(MAX_PLAYERS + 1))

    with pytest.raises(PlayersCountExceedMaxPlayersCountError) as exc_info:
        game.start()

    assert exc_info.value.message == 'Players count exceed max players count %s' % str(
        MAX_PLAYERS
    )
