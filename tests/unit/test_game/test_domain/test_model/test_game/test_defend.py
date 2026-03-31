import pytest

from durak.game.domain.exceptions import (
    OnlyDefenderCanDefendError,
    PlayerAlreadyPassedError,
    PlayerDoesntHaveCardError,
)
from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.game import (
    Game,
)
from durak.game.domain.model.turn import Turn, TurnPair


def test_defend_success(get_players):
    players = get_players(3)

    attack = Card(rank=Rank.NINE, suit=Suit.SPADES)
    defense = Card(rank=Rank.QUEEN, suit=Suit.SPADES)

    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(
            pairs=[TurnPair(attack_card=attack)], passed_players=[players[0].id_]
        ),
    )
    game.start()

    game.defender.hand.append(defense)

    game.defend(game.defender, attack, defense)

    assert game.turn.pairs[0].defense_card == defense
    assert defense not in game.defender.hand
    assert game.turn.passed_players == []


def test_defend_raises_only_defender_can_defend(get_players):
    players = get_players(3)

    attack = Card(rank=Rank.EIGHT, suit=Suit.SPADES)
    defense = Card(rank=Rank.NINE, suit=Suit.SPADES)

    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(pairs=[TurnPair(attack_card=attack)]),
    )
    game.start()

    # Put defense card to defender (not used in this test logic)
    game.defender.hand.append(defense)

    with pytest.raises(OnlyDefenderCanDefendError) as exc_info:
        game.defend(players[0], attack, defense)

    assert exc_info.value.message == 'Only defender can defend'


def test_defend_raises_when_player_already_passed(get_players):
    players = get_players(3)

    attack = Card(rank=Rank.TEN, suit=Suit.CLUBS)
    defense = Card(rank=Rank.JACK, suit=Suit.CLUBS)

    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(
            pairs=[TurnPair(attack_card=attack)], passed_players=[players[1].id_]
        ),
    )
    game.start()

    game.defender.hand.append(defense)

    with pytest.raises(PlayerAlreadyPassedError) as exc_info:
        game.defend(game.defender, attack, defense)

    assert exc_info.value.message == 'Player already passed % s' % str(game.defender)


def test_defend_raises_when_player_doesnt_have_card(get_players):
    players = get_players(3)

    attack = Card(rank=Rank.SEVEN, suit=Suit.DIAMONDS)
    defense = Card(rank=Rank.QUEEN, suit=Suit.DIAMONDS)

    game = Game(
        players=players,
        first_defender_id=players[1].id_,
        turn=Turn(pairs=[TurnPair(attack_card=attack)]),
    )
    game.start()

    # Do NOT add defense card to defender hand

    with pytest.raises(PlayerDoesntHaveCardError) as exc_info:
        game.defend(game.defender, attack, defense)

    assert exc_info.value.message == 'Player doesnt have this card %s' % str(defense)
