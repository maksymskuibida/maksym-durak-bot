from durak.game.domain.model.card import Card, Rank, Suit
from tests.factories.base import Factory


class CardFactory(Factory[Card]):
    class Meta:
        model = Card

    rank = Rank.ACE
    suit = Suit.SPADES
