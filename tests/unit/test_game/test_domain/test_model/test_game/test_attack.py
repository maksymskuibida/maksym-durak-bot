import pytest

from durak.game.domain.exceptions import (
    DefenderHasNoMoreCardsLeftError,
    FirstAttackHasToBeFromThePlayerLeftError,
    PlayerAlreadyPassedError,
    PlayerDoesntHaveCardError,
)
from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.game import Game
from durak.game.domain.model.turn import Turn, TurnPair
from tests.factories.game.card import CardFactory
from tests.factories.game.player import PlayerFactory


def test_attack_success_first_attacker_on_empty_turn_adds_pair(get_players):
    # Arrange: create a game with 3 players and pick middle one as defender
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[1].id_)
    game.start()

    first_attacker = game.first_attacker  # should be players[0]

    attack_card = CardFactory.build()

    first_attacker.hand.append(attack_card)

    # Act
    game.attack(first_attacker, attack_card)

    # Assert
    assert len(game.turn.pairs) == 1
    assert game.turn.pairs[0].attack_card == attack_card
    assert game.turn.pairs[0].defense_card is None
    assert game.turn.passed_players == []


def test_attack_success_not_first_attacker_on_not_empty_turn_adds_pair(get_players):
    # Arrange: create a game with 3 players and pick the middle one as defender
    players = get_players(3)
    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(pairs=[TurnPair(attack_card=Card(rank=Rank.ACE, suit=Suit.SPADES))]),
    )
    game.start()

    attacker = game.players[2]  # should be players[0]

    attack_card = Card(rank=Rank.ACE, suit=Suit.DIAMONDS)

    attacker.hand.append(attack_card)

    # Act
    game.attack(attacker, attack_card)

    # Assert
    assert len(game.turn.pairs) == 2
    assert game.turn.pairs[1].attack_card == attack_card
    assert game.turn.pairs[1].defense_card is None
    assert game.turn.passed_players == []


def test_attack_raises_when_wrong_player_starts_on_empty_turn(get_players):
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[1].id_)
    game.start()

    wrong_attacker = players[2]  # not the player to the left of defender
    attack_card = CardFactory.build()

    with pytest.raises(FirstAttackHasToBeFromThePlayerLeftError) as exc_info:
        game.attack(wrong_attacker, attack_card)

    assert exc_info.value.message == 'first attack has to be from the player left'


def test_attack_raises_when_defender_has_no_more_cards_left(get_players):
    # Defender has 2 cards in hand
    players = get_players(3)
    game = Game(players=players, first_defender_id=players[1].id_)
    game.start()

    defender = game.defender
    # Manually assign 2 cards to defender's hand after start
    defender.hand = [CardFactory.build(), CardFactory.build()]

    # Pre-populate turn with the same number of attack pairs as defender's cards
    game.turn.pairs = [
        TurnPair(attack_card=CardFactory.build()) for _ in range(defender.cards_in_hand)
    ]

    attacker = players[0]
    attack_card = CardFactory.build()

    with pytest.raises(DefenderHasNoMoreCardsLeftError) as exc_info:
        game.attack(attacker, attack_card)

    assert exc_info.value.message == 'defender has no more cards left'


def test_attack_raises_when_player_doesnt_have_card(get_players):
    # Arrange: create a game with 3 players and pick the middle one as defender
    players = get_players(3)
    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(pairs=[TurnPair(attack_card=Card(rank=Rank.ACE, suit=Suit.SPADES))]),
    )
    game.start()

    attacker = game.players[2]  # should be players[0]

    attack_card = Card(rank=Rank.ACE, suit=Suit.DIAMONDS)

    with pytest.raises(PlayerDoesntHaveCardError) as exc_info:
        game.attack(attacker, attack_card)

    assert exc_info.value.message == 'Player doesnt have this card %s' % str(
        attack_card
    )


def test_attack_raises_when_player_passed(get_players):
    # Defender has 2 cards in hand
    players = get_players(3)

    defender = players[1]
    attacker = players[0]

    game = Game(
        players=players,
        first_defender_id=defender.id_,
        turn=Turn(
            pairs=[TurnPair(attack_card=CardFactory.build()) for _ in range(2)],
            passed_players=[attacker.id_],
        ),
    )
    game.start()

    # Set defender hand after start
    game.defender.hand = [CardFactory.build(), CardFactory.build()]

    attack_card = CardFactory.build()

    with pytest.raises(PlayerAlreadyPassedError) as exc_info:
        game.attack(attacker, attack_card)

    assert exc_info.value.message == 'Player already passed % s' % str(attacker)
