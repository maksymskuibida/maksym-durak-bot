import pytest

from durak.game.domain.model.card import Rank
from durak.game.domain.model.player import PlayerStatus
from tests.factories.game.card import CardFactory
from tests.factories.game.player import PlayerFactory


def test_create_player():
    player = PlayerFactory.build()

    assert player.name == 'Player #0'
    assert player.hand == []


def test_it_adds_a_card_to_hand():
    player = PlayerFactory.build()
    card = CardFactory.build()
    player.take_cards(card)

    assert player.hand == [card]


def test_it_removes_a_card_from_hand():
    card = CardFactory.build()
    player = PlayerFactory.build(hand=[card])

    assert player.cards_in_hand == 1

    player.discard_card(card)

    assert player.hand == []


def test_it_checks_if_hand_is_empty():
    player = PlayerFactory.build()

    assert player.is_empty_hand

    card = CardFactory()
    player.take_cards(card)

    assert not player.is_empty_hand


@pytest.mark.parametrize(
    ('card_to_check', 'expected_result'),
    ((CardFactory.build(), True), (CardFactory.build(rank=Rank.SIX), False)),
)
def test_has_card(card_to_check, expected_result):
    player = PlayerFactory.build(hand=[CardFactory.build()])
    assert player.has_card(card_to_check) == expected_result


@pytest.mark.parametrize(
    ('status', 'expected_result'),
    (
        (PlayerStatus.IN_GAME, True),
        (PlayerStatus.FINISHED, False),
        (PlayerStatus.LOST, False),
    ),
)
def test_in_game(status, expected_result):
    player = PlayerFactory.build(status=status)
    assert player.is_in_game == expected_result
