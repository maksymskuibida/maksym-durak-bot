from enum import IntEnum, StrEnum

from durak.shared.domain.model.base import ValueObject


class Rank(IntEnum):
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


RANKS_MAPPING = {
    Rank.SIX: '6',
    Rank.SEVEN: '7',
    Rank.EIGHT: '8',
    Rank.NINE: '9',
    Rank.TEN: '10',
    Rank.JACK: 'J',
    Rank.QUEEN: 'Q',
    Rank.KING: 'K',
    Rank.ACE: 'A',
}


class Suit(StrEnum):
    CLUBS = 'clubs'
    DIAMONDS = 'diamonds'
    HEARTS = 'hearts'
    SPADES = 'spades'


SUITS_MAPPING = {
    Suit.CLUBS: '♣️',
    Suit.DIAMONDS: '♦️',
    Suit.HEARTS: '♥️',
    Suit.SPADES: '♠️',
}


class Card(ValueObject):
    rank: Rank
    suit: Suit

    def __str__(self):
        return SUITS_MAPPING[self.suit] + RANKS_MAPPING[self.rank]


MAX_CARDS = len(Rank) * len(Suit)
