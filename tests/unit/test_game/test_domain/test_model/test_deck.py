import pytest

from durak.game.domain.exceptions import TrumpHasNotBeenPickedError
from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.deck import (
    Deck,
    EmptyDeckError,
)
from tests.factories.game.card import CardFactory


def test_create_deck():
    deck = Deck()

    # Expected order: for each suit in Suit, ranks in ascending order
    expected = [Card(rank=rank, suit=suit) for suit in Suit for rank in Rank]

    assert len(deck.cards) == 36
    assert len(set(deck.cards)) == 36
    assert deck.cards == expected


def test_it_shuffles_cards():
    deck = Deck()
    original_cards = deck.cards.copy()
    deck.shuffle()
    assert original_cards != deck.cards


def test_it_draws_a_card():
    deck = Deck()
    card = deck.draw()
    assert card not in deck.cards
    assert card == CardFactory.build()
    assert len(deck.cards) == 35


def test_it_raises_error_when_deck_is_empty():
    deck = Deck(cards=[])

    with pytest.raises(EmptyDeckError) as exc_info:
        deck.draw()

    assert exc_info.value.message == 'Deck is empty'


def test_trump_card_raises_before_pick():
    deck = Deck()

    with pytest.raises(TrumpHasNotBeenPickedError) as exc_info:
        _ = deck.trump_card

    assert exc_info.value.message == 'Trump has not been picked yet'


def test_pick_trump_sets_and_places_card():
    deck = Deck()
    original_set = set(deck.cards)

    assert deck._trump_picked is False

    trump = deck.pick_trump()

    assert deck._trump_picked is True

    # The picked trump must now be accessible and placed as the last card
    assert deck.trump_card == trump
    assert deck.cards[-1] == trump

    # No cards are lost or duplicated
    assert len(deck.cards) == 36
    assert set(deck.cards) == original_set
