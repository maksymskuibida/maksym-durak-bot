import random

from pydantic import Field

from durak.game.domain.exceptions import TrumpHasNotBeenPickedError
from durak.game.domain.model.card import Card, Rank, Suit
from durak.shared.domain.exceptions import DomainError
from durak.shared.domain.model.base import DataObject


class Deck(DataObject):
    cards: list[Card] = Field(
        default_factory=lambda: [
            Card(rank=rank, suit=suit) for suit in Suit for rank in Rank
        ],
    )

    _trump_picked: bool = False

    @property
    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def draw(self) -> Card:
        if self.is_empty:
            raise EmptyDeckError()
        return self.cards.pop()

    def shuffle(self):
        random.shuffle(self.cards)

    @property
    def cards_count(self) -> int:
        return len(self.cards)

    @property
    def trump_card(self):
        if not self._trump_picked:
            raise TrumpHasNotBeenPickedError()
        return self.cards[-1]

    def pick_trump(self):
        trump_card = random.choice(self.cards)
        self._trump_picked = True
        self.cards.remove(trump_card)
        self.cards.append(trump_card)
        return trump_card


class EmptyDeckError(DomainError):
    message = 'Deck is empty'
