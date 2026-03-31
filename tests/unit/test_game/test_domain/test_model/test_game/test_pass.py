import pytest

from durak.game.domain.exceptions import (
    DefenderCannotPassError,
    PlayerAlreadyPassedError,
)
from durak.game.domain.model.game import Game
from durak.game.domain.model.player import PlayerStatus
from tests.factories.game.game import GameFactory


def test_check_if_all_players_passed(get_players):
    game = GameFactory.build(players=get_players(3))
    game.start()

    assert game.defender.id_ == game.players[0].id_

    # check it returns False if all players are active and not passed
    assert not game._check_if_all_players_passed()

    game.turn.pass_(game.players[1].id_)
    # check it returns False if one player passed
    assert not game._check_if_all_players_passed()

    game.turn.pass_(game.players[2].id_)
    # check it returns False if all players passed
    assert game._check_if_all_players_passed()

    game.turn.passed_players.clear()

    game.players[2].set_status(PlayerStatus.FINISHED)

    # check it returns False if one player is out and other didn't pass
    assert not game._check_if_all_players_passed()

    game.turn.pass_(game.players[1].id_)

    # check it returns True if one player is out and other passed
    assert game._check_if_all_players_passed()


def test_pass_adds_player_to_passed_list(get_players):
    # Arrange
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[0].id_)
    game.start()

    player = players[1]

    game.pass_(player)

    assert player.id_ in game.turn.passed_players


def test_pass_raises_when_defender_attempts_to_pass(get_players):
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[0].id_)
    game.start()

    defender = game.defender

    with pytest.raises(DefenderCannotPassError) as exc_info:
        game.pass_(defender)

    assert exc_info.value.message == 'Defender cannot pass'


def test_pass_raises_when_player_already_passed(get_players):
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[0].id_)
    game.start()

    attacker = players[1]
    game.turn.passed_players = [attacker.id_]

    with pytest.raises(PlayerAlreadyPassedError) as exc_info:
        game.pass_(attacker)

    assert exc_info.value.message == 'Player already passed % s' % str(attacker)


def test_pass_calls_end_turn_when_all_attackers_passed(get_players, monkeypatch):
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[0].id_)
    game.start()

    # Pre-mark one non-defender as passed; the next pass should complete the set
    already_passed = players[2]
    game.turn.passed_players = [already_passed.id_]

    called = {"v": False}

    def fake_end_turn(self):  # noqa: ARG001
        called["v"] = True

    monkeypatch.setattr(Game, "_end_turn", fake_end_turn)

    attacker = players[1]
    game.pass_(attacker)

    assert called["v"] is True


def test_pass_does_not_call_end_turn_when_not_all_attackers_passed(
    get_players, monkeypatch
):
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[0].id_)
    game.start()

    end_turn_called = False

    def fake_end_turn(self):  # noqa: ARG001
        nonlocal end_turn_called
        end_turn_called = True

    monkeypatch.setattr(Game, "_end_turn", fake_end_turn)

    attacker = players[1]
    game.pass_(attacker)

    assert end_turn_called is False
