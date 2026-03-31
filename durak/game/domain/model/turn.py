from pydantic import Field

from durak.game.domain.exceptions import (
    CannotDefendWithDifferentSuitError,
    CannotDefendWithLowerRankError,
    NoPairFoundError,
    PairIsAlreadyDefendedError,
    RankIsNotinTheTurnError,
)
from durak.game.domain.model.card import Card, Rank, Suit
from durak.shared.domain.model.base import DataObject


class TurnPair(DataObject):
    attack_card: Card
    defense_card: Card | None = None

    def defend(self, defense_card: Card):
        self.defense_card = defense_card


class Turn(DataObject):
    pairs: list[TurnPair] = Field(default_factory=list)
    passed_players: list[str] = Field(default_factory=list)

    @property
    def is_started(self):
        return len(self.pairs) != 0

    @property
    def all_cards(self) -> list[Card]:
        cards: list[Card] = []
        for pair in self.pairs:
            cards.append(pair.attack_card)
            if pair.defense_card:
                cards.append(pair.defense_card)
        return cards

    @property
    def allowed_ranks(self) -> set[Rank]:
        return set(card.rank for card in self.all_cards)

    def attack(self, attack_card: Card):
        if self.pairs and attack_card.rank not in self.allowed_ranks:
            raise RankIsNotinTheTurnError(attack_card.rank)

        self.pairs.append(TurnPair(attack_card=attack_card))
        self.passed_players.clear()

    def defend(self, attack_card: Card, defense_card: Card, trump: Suit):
        pair = next(
            (pair for pair in self.pairs if pair.attack_card == attack_card), None
        )
        if not pair:
            raise NoPairFoundError(attack_card)

        if pair.defense_card:
            raise PairIsAlreadyDefendedError(attack_card)

        if defense_card.suit == attack_card.suit:
            if defense_card.rank <= attack_card.rank:
                raise CannotDefendWithLowerRankError(attack_card, defense_card, trump)
        elif defense_card.suit != trump:
            raise CannotDefendWithDifferentSuitError(attack_card, defense_card, trump)
        pair.defend(defense_card)
        self.passed_players.clear()

    def is_player_passed(self, player_id: str) -> bool:
        return player_id in self.passed_players

    def pass_(self, player_id: str):
        self.passed_players.append(player_id)

    def end(self):
        self.pairs.clear()
        self.passed_players.clear()
