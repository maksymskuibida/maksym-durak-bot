import pytest

from durak.game.domain.exceptions import (
    OnlyDefenderCanTakeCardsError,
    TurnIsNotStaredYetError,
)
from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.game import Game
from durak.game.domain.model.turn import Turn, TurnPair


def test_take_cards_raises_when_turn_not_started(get_players):
    # Arrange: game is started but no attacks yet (empty turn)
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[0].id_)
    game.start()

    with pytest.raises(TurnIsNotStaredYetError) as exc_info:
        game.take_cards(game.defender)

    assert exc_info.value.message == 'Turn is not started yet'


def test_take_cards_raises_when_non_defender_calls(get_players):
    # Arrange: prepare a started turn so first precondition passes
    players = get_players(3)
    attack = Card(rank=Rank.SEVEN, suit=Suit.HEARTS)
    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(pairs=[TurnPair(attack_card=attack)]),
    )
    game.start()

    non_defender = players[0]

    with pytest.raises(OnlyDefenderCanTakeCardsError) as exc_info:
        game.take_cards(non_defender)

    assert exc_info.value.message == 'Only defender can take cards'


def test_take_cards_success_adds_all_turn_cards_and_ends_turn(get_players, monkeypatch):
    # Arrange: a turn with two pairs (one defended) so defender should take 2 or 3 cards
    players = get_players(3)

    attacker_1 = Card(rank=Rank.SIX, suit=Suit.CLUBS)
    attacker_2 = Card(rank=Rank.SEVEN, suit=Suit.CLUBS)
    defender_2 = Card(rank=Rank.EIGHT, suit=Suit.CLUBS)

    turn = Turn(
        pairs=[
            TurnPair(attack_card=attacker_1),
            TurnPair(attack_card=attacker_2, defense_card=defender_2),
        ]
    )

    game = Game(players=players, first_defender_id=players[1].id_, turn=turn)
    game.start()

    end_turn_called = False

    def fake_end_turn(self):  # noqa: ARG001
        nonlocal end_turn_called
        end_turn_called = True

    monkeypatch.setattr(Game, "_end_turn", fake_end_turn)

    defender = game.defender
    initial_hand_size = len(defender.hand)
    expected_taken = len(game.turn.all_cards)

    game.take_cards(defender)

    # Assert: defender received all cards from the tur}}n, and _end_turn was called
    assert len(defender.hand) == initial_hand_size + expected_taken
    assert all(card in defender.hand for card in [attacker_1, attacker_2, defender_2])
    assert end_turn_called
