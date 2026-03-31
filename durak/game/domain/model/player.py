from enum import StrEnum

from pydantic import Field

from durak.game.domain.model.card import Card
from durak.shared.domain.model.base import Entity


class PlayerStatus(StrEnum):
    IN_GAME = 'in_game'
    FINISHED = 'finished'
    LOST = 'lost'


class Player(Entity):
    name: str
    hand: list[Card] = Field(default_factory=list)
    status: PlayerStatus = PlayerStatus.IN_GAME

    def __str__(self):
        return self.name + f' ({self.id_})'

    def take_cards(self, *cards: Card):
        self.hand.extend(cards)

    def discard_card(self, card: Card):
        self.hand.remove(card)

    def has_card(self, card: Card) -> bool:
        return card in self.hand

    @property
    def cards_in_hand(self) -> int:
        return len(self.hand)

    @property
    def is_empty_hand(self) -> bool:
        return self.cards_in_hand == 0

    @property
    def is_in_game(self):
        return self.status == PlayerStatus.IN_GAME

    def set_status(self, status: PlayerStatus):
        self.status = status
