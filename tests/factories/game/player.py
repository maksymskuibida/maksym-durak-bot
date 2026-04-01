from durak.game.domain.model.player import Player
from tests.factories.base import Factory, NamedSequence

from ..base import IDSequence


class PlayerFactory(Factory[Player]):
    class Meta:
        model = Player

    id_ = IDSequence('ID')
    user_id = IDSequence('UserID')
    name = NamedSequence('Player')
