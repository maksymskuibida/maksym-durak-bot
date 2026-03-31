from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from functools import wraps
from typing import TypeVar

from pydantic import Field

from durak.game.domain.constants import HAND_SIZE
from durak.game.domain.exceptions import (
    AtLeast2PlayersRequiredError,
    DefenderCannotPassError,
    DefenderHasNoMoreCardsLeftError,
    DefenderHasNotBeenPickedError,
    FirstAttackHasToBeFromThePlayerLeftError,
    GameIsAlreadyFinishedError,
    GameIsAlreadyInProgressError,
    GameIsNotStartedYetError,
    OnlyDefenderCanDefendError,
    OnlyDefenderCanTakeCardsError,
    PlayerAlreadyPassedError,
    PlayerDoesntHaveCardError,
    PlayerIsAlreadyInTheGameError,
    PlayerNotFoundError,
    PlayersCountExceedMaxPlayersCountError,
    TurnIsNotStaredYetError,
)
from durak.game.domain.model.card import Card, MAX_CARDS, Rank, Suit
from durak.game.domain.model.deck import Deck
from durak.game.domain.model.player import Player, PlayerStatus
from durak.game.domain.model.turn import Turn
from durak.shared.domain.model.base import Entity
from durak.shared.utils.date_time import utcnow

MAX_PLAYERS = MAX_CARDS // HAND_SIZE


class GameStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


T = TypeVar('T')


GAME_STATUS_ERRORS = {
    GameStatus.PENDING: GameIsNotStartedYetError,
    GameStatus.IN_PROGRESS: GameIsAlreadyInProgressError,
    GameStatus.FINISHED: GameIsAlreadyFinishedError,
}


def _validate_game_status(game: Game, expected_status: GameStatus):
    if game.status != expected_status:
        raise GAME_STATUS_ERRORS[game.status]


def check_game_status(expected_status: GameStatus):
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(game: Game, *args, **kwargs):
            _validate_game_status(game, expected_status)
            return func(game, *args, **kwargs)

        return wrapper

    return decorator


class Game(Entity):
    created_at: datetime = Field(default_factory=utcnow)
    status: GameStatus = GameStatus.PENDING

    players: list[Player] = Field(default_factory=list)
    deck: Deck = Field(default_factory=Deck)
    turn: Turn = Field(default_factory=Turn)

    defender_id: str | None = None
    first_defender_id: str | None = None

    @property
    def trump(self) -> Suit:
        return self.deck.trump_card.suit

    @property
    def main_player(self):
        return self.players[0]

    @property
    def active_players(self) -> list[Player]:
        return list(filter(lambda player: player.is_in_game, self.players))

    @property
    def defender(self) -> Player:
        if not self.defender_id:
            raise DefenderHasNotBeenPickedError()
        return next(player for player in self.players if player.id_ == self.defender_id)

    @property
    def first_attacker(self) -> Player:
        defender_idx = self.active_players.index(self.defender)
        return self.active_players[defender_idx - 1]

    def is_player_in_game(self, player_id: str):
        return next((p for p in self.players if p.id_ == player_id), None)

    @check_game_status(GameStatus.PENDING)
    def add_player(self, player: Player):
        if len(self.players) >= MAX_PLAYERS:
            raise PlayersCountExceedMaxPlayersCountError(MAX_PLAYERS)

        if self.is_player_in_game(player.id_):
            raise PlayerIsAlreadyInTheGameError(player)

        self.players.append(player)

    @check_game_status(GameStatus.PENDING)
    def remove_player(self, player: Player):
        if player not in self.players:
            raise PlayersCountExceedMaxPlayersCountError(MAX_PLAYERS)

        if not self.is_player_in_game(player.id_):
            raise PlayerNotFoundError(player.id_)

        self.players.append(player)

    def _deal_first_cards(self):
        for _ in range(HAND_SIZE):
            for player in self.players:
                player.take_cards(self.deck.draw())

    def _pick_first_defender(self) -> str | None:
        if self.first_defender_id:
            if not self.is_player_in_game(self.first_defender_id):
                raise PlayerNotFoundError(self.first_defender_id)
            return self.first_defender_id

        # iterate through rank from low to top to define the player with the lowest trump
        for rank in Rank:
            for i, player in enumerate(self.players):
                for card in player.hand:
                    if card.suit == self.trump and card.rank == rank:
                        return self.players[i].id_

        return self.players[0].id_

    def start(self):
        _validate_game_status(self, GameStatus.PENDING)

        if len(self.players) < 2:
            raise AtLeast2PlayersRequiredError()
        if len(self.players) > MAX_PLAYERS:
            raise PlayersCountExceedMaxPlayersCountError(MAX_PLAYERS)

        self.status = GameStatus.IN_PROGRESS

        self.deck.shuffle()
        self._deal_first_cards()
        self.deck.pick_trump()

        self.defender_id = self._pick_first_defender()

        return self

    @classmethod
    def create_game(cls, player: Player, first_defender: str | None = None):
        return cls(players=[player], first_defender_id=first_defender)

    @check_game_status(GameStatus.IN_PROGRESS)
    def attack(self, player: Player, attack_card: Card):
        if not self.turn.is_started and player.id_ != self.first_attacker.id_:
            raise FirstAttackHasToBeFromThePlayerLeftError()

        if self.turn.is_player_passed(player.id_):
            raise PlayerAlreadyPassedError(player)

        if len(self.turn.pairs) == self.defender.cards_in_hand:
            raise DefenderHasNoMoreCardsLeftError()

        if not player.has_card(attack_card):
            raise PlayerDoesntHaveCardError(attack_card)

        self.turn.attack(attack_card)
        player.discard_card(attack_card)

    @check_game_status(GameStatus.IN_PROGRESS)
    def defend(self, player: Player, attack_card: Card, defense_card: Card):
        if player.id_ != self.defender.id_:
            raise OnlyDefenderCanDefendError()

        if self.turn.is_player_passed(player.id_):
            raise PlayerAlreadyPassedError(player)

        if not player.has_card(defense_card):
            raise PlayerDoesntHaveCardError(defense_card)
        self.turn.defend(attack_card, defense_card, self.trump)
        player.discard_card(defense_card)

    def _deal_cards_after_turn(self):
        for player in self.active_players:
            # exit, if deck is empty
            if self.deck.is_empty:
                break

            needed_cards = HAND_SIZE - len(player.hand)
            if needed_cards > 0:
                player.take_cards(
                    *[
                        self.deck.draw()
                        # ensure we don't try to draw more cards that exist in deck
                        for _ in range(min(needed_cards, self.deck.cards_count))
                    ]
                )

    def _set_empty_handed_players_to_finish(self):
        for player in self.players:
            if player.is_empty_hand:
                player.set_status(PlayerStatus.FINISHED)

    def _rotate_defender(self):
        defender_idx = self.players.index(self.defender)
        next_player_idx = defender_idx + 1

        while next_player_idx != defender_idx:
            # wrap, if index exceeds max index in self.players
            if next_player_idx >= len(self.players):
                next_player_idx %= len(self.players)

            # skip the player if it is not active already
            if not self.players[next_player_idx].is_in_game:
                next_player_idx += 1
                continue

            # set new defender_id if the player is active
            self.defender_id = self.players[next_player_idx].id_
            return

    def _finish(self):
        self.status = GameStatus.FINISHED
        self.active_players[0].set_status(PlayerStatus.LOST)

    def _end_turn(self):
        self.turn.end()
        self._deal_cards_after_turn()
        self._set_empty_handed_players_to_finish()
        self._rotate_defender()

        # finish the game if only one active player left
        if len(self.active_players) == 1:
            self._finish()

    def _check_if_all_players_passed(self) -> bool:
        return all(
            self.turn.is_player_passed(player.id_) or player.id_ == self.defender.id_
            for player in self.active_players
        )

    @check_game_status(GameStatus.IN_PROGRESS)
    def pass_(self, player: Player):
        if self.turn.is_player_passed(player.id_):
            raise PlayerAlreadyPassedError(player)

        if player.id_ == self.defender.id_:
            raise DefenderCannotPassError()

        self.turn.pass_(player.id_)

        if self._check_if_all_players_passed():
            self._end_turn()

    @check_game_status(GameStatus.IN_PROGRESS)
    def take_cards(self, player: Player):
        if not self.turn.is_started:
            raise TurnIsNotStaredYetError()

        if player.id_ != self.defender.id_:
            raise OnlyDefenderCanTakeCardsError()

        player.take_cards(*self.turn.all_cards)
        self._end_turn()
