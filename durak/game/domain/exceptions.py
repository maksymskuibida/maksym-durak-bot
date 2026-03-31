from typing import Any

from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.player import Player
from durak.shared.domain.exceptions import DomainError


class GameError(DomainError):
    pass


class GameErrorWithMessageParams(GameError):
    def __init__(self, message: str | None = None, *, params: str | tuple[Any, ...]):
        self.message = (
            self.resolve_message(message) % params
            if isinstance(params, str)
            else tuple(str(param) for param in params)
        )


class GameIsNotStartedYetError(GameError):
    message = 'Game is not started yet'


class GameIsAlreadyInProgressError(GameError):
    message = 'Game is already in progress'


class GameIsAlreadyFinishedError(GameError):
    message = 'Game is already finished'


class AtLeast2PlayersRequiredError(GameError):
    message = 'At least 2 players required'


class PlayersCountExceedMaxPlayersCountError(GameErrorWithMessageParams):
    message = 'Players count exceed max players count %s'

    def __init__(self, max_count: int):
        self.max_count = max_count

        super().__init__(params=str(self.max_count))


class PlayerIsAlreadyInTheGameError(GameErrorWithMessageParams):
    message = 'Player %s is already in the game'

    def __init__(self, player: Player):
        self.player = player

        super().__init__(params=str(self.player))


class PlayerNotFoundError(GameErrorWithMessageParams):
    message = 'Player with id %s not found'

    def __init__(self, player_id: str):
        self.player_id = player_id

        super().__init__(params=player_id)


class DefenderHasNotBeenPickedError(GameError):
    message = 'Defender has not been picked yet'


class TrumpHasNotBeenPickedError(GameError):
    message = 'Trump has not been picked yet'


class PlayerDoesntHaveCardError(GameErrorWithMessageParams):
    message = 'Player doesnt have this card %s'

    def __init__(self, card: Card):
        self.card = card
        super().__init__(params=str(card))


class NoPairFoundError(GameErrorWithMessageParams):
    message = 'No pair with attack card %s found'

    def __init__(self, attack_card: Card):
        self.attack_card = attack_card
        super().__init__(params=str(attack_card))


class PairIsAlreadyDefendedError(GameErrorWithMessageParams):
    message = 'Pair is already defended. Attack card: %s'

    def __init__(self, attack_card: Card):
        self.attack_card = attack_card
        super().__init__(params=str(attack_card))


class DefenceError(GameErrorWithMessageParams):
    def __init__(self, attack_card: Card, defense_card: Card, trump: Suit):
        self.attack_card = attack_card
        self.defense_card = defense_card
        self.trump = trump

        super().__init__(params=(self.attack_card, self.defense_card, self.trump))


class CannotDefendWithDifferentSuitError(DefenceError):
    message = 'Cannot defend with different suit. Attack card: %s, Defence card: %s. Trump: %s'


class CannotDefendWithLowerRankError(DefenceError):
    message = (
        'Cannot defend with lower rank. Attack card: %s, Defence card: %s. Trump: %s'
    )


class FirstAttackHasToBeFromThePlayerLeftError(GameError):
    message = 'first attack has to be from the player left'


class DefenderHasNoMoreCardsLeftError(GameError):
    message = 'defender has no more cards left'


class RankIsNotinTheTurnError(GameErrorWithMessageParams):
    message = 'Rank %s is not in the turn'

    def __init__(self, rank: Rank):
        self.rank = rank
        super().__init__(params=str(rank))


class OnlyDefenderCanDefendError(GameError):
    message = 'Only defender can defend'


class OnlyDefenderCanTakeCardsError(GameError):
    message = 'Only defender can take cards'


class PlayerAlreadyPassedError(GameErrorWithMessageParams):
    message = 'Player already passed % s'

    def __init__(self, player: Player):
        self.player = player
        super().__init__(params=str(player))


class DefenderCannotPassError(GameError):
    message = 'Defender cannot pass'


class TurnIsNotStaredYetError(GameError):
    message = 'Turn is not started yet'
