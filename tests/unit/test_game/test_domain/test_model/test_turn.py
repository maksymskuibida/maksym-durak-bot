import pytest

from durak.game.domain.exceptions import (
    CannotDefendWithDifferentSuitError,
    CannotDefendWithLowerRankError,
    NoPairFoundError,
    PairIsAlreadyDefendedError,
    RankIsNotinTheTurnError,
)
from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.turn import (
    Turn,
    TurnPair,
)
from tests.factories.game.card import CardFactory
from tests.factories.game.turn import TurnFactory


def test_attack_adds_new_pair():
    turn = Turn()
    assert turn.pairs == []

    attack = CardFactory.build()

    turn.attack(attack)

    assert len(turn.pairs) == 1
    assert turn.pairs[0].attack_card == attack
    assert turn.pairs[0].defense_card is None


def test_attack_raises_when_rank_not_on_the_turn():
    # Given a non-empty turn with some allowed ranks
    turn = TurnFactory.build()
    assert turn.is_started
    allowed = turn.allowed_ranks

    # Pick any rank that is not currently on the turn
    rank_not_on_turn = next(r for r in Rank if r not in allowed)

    # When attacking with a card whose rank is not on the turn
    # Then it should raise RankIsNotinTheTurnError
    with pytest.raises(RankIsNotinTheTurnError) as exc_info:
        turn.attack(Card(rank=rank_not_on_turn, suit=Suit.HEARTS))

    assert exc_info.value.message == 'Rank %s is not in the turn' % str(
        rank_not_on_turn
    )


def test_defend_with_same_suit_higher_rank():
    attack = Card(rank=Rank.NINE, suit=Suit.HEARTS)
    defense = Card(rank=Rank.QUEEN, suit=Suit.HEARTS)
    trump = Suit.SPADES

    turn = Turn(pairs=[TurnPair(attack_card=attack)])

    turn.defend(attack_card=attack, defense_card=defense, trump=trump)

    assert turn.pairs[0].defense_card == defense


def test_defend_with_trump_over_non_trump():
    attack = Card(rank=Rank.KING, suit=Suit.CLUBS)
    defense = Card(rank=Rank.SIX, suit=Suit.DIAMONDS)
    trump = Suit.DIAMONDS

    turn = Turn(pairs=[TurnPair(attack_card=attack)])

    turn.defend(attack_card=attack, defense_card=defense, trump=trump)

    assert turn.pairs[0].defense_card == defense


def test_defend_raises_when_no_pair_found():
    turn = Turn()
    attack = Card(rank=Rank.SEVEN, suit=Suit.SPADES)
    defense = Card(rank=Rank.ACE, suit=Suit.SPADES)

    with pytest.raises(NoPairFoundError):
        turn.defend(attack_card=attack, defense_card=defense, trump=Suit.HEARTS)


def test_defend_raises_when_pair_already_defended():
    turn = Turn(
        pairs=[
            TurnPair(
                attack_card=Card(rank=Rank.EIGHT, suit=Suit.CLUBS),
                defense_card=Card(rank=Rank.TEN, suit=Suit.CLUBS),
            )
        ]
    )

    with pytest.raises(PairIsAlreadyDefendedError):
        turn.defend(
            attack_card=turn.pairs[0].attack_card,
            defense_card=Card(rank=Rank.ACE, suit=Suit.CLUBS),
            trump=Suit.SPADES,
        )


def test_defend_raises_when_different_suit_and_not_trump():
    attack = Card(rank=Rank.JACK, suit=Suit.HEARTS)
    defense = Card(rank=Rank.ACE, suit=Suit.SPADES)

    turn = Turn(pairs=[TurnPair(attack_card=attack)])
    trump = Suit.DIAMONDS

    with pytest.raises(CannotDefendWithDifferentSuitError):
        turn.defend(attack_card=attack, defense_card=defense, trump=trump)


@pytest.mark.parametrize(
    "attack_rank, defense_rank",
    [
        (Rank.QUEEN, Rank.JACK),  # lower rank
        (Rank.NINE, Rank.NINE),  # equal rank
    ],
)
def test_defend_raises_when_same_suit_lower_or_equal_rank(attack_rank, defense_rank):
    attack = Card(rank=attack_rank, suit=Suit.SPADES)
    defense = Card(rank=defense_rank, suit=Suit.SPADES)

    turn = Turn(pairs=[TurnPair(attack_card=attack)])

    with pytest.raises(CannotDefendWithLowerRankError):
        turn.defend(attack_card=attack, defense_card=defense, trump=Suit.HEARTS)


def test_turn_pair_defend_sets_defense_card():
    attack = CardFactory.build()
    defense = Card(rank=Rank.SIX, suit=attack.suit)
    pair = TurnPair(attack_card=attack)

    assert pair.defense_card is None

    pair.defend(defense)

    assert pair.defense_card == defense


@pytest.mark.parametrize(
    ('player_id', 'expected_result'),
    (
        ('Player-1', True),
        ('Player-2', False),
    ),
)
def test_is_player_passed(player_id, expected_result):
    turn = TurnFactory.build(passed_players=['Player-1'])
    assert turn.is_player_passed(player_id) == expected_result


def test_pass():
    turn = TurnFactory.build()
    assert len(turn.passed_players) == 0
    turn.pass_('Player-1')
    assert len(turn.passed_players) == 1


def test_turn_end():
    turn = TurnFactory.build(passed_players=['Player-1'])
    assert len(turn.pairs) == 1
    assert len(turn.passed_players) == 1
    turn.end()
    assert len(turn.pairs) == 0
    assert len(turn.passed_players) == 0
