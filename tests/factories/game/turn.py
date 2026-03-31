import factory

from durak.game.domain.model.turn import Turn, TurnPair
from tests.factories.base import Factory
from tests.factories.game.card import CardFactory


class TurnPairFactory(Factory[TurnPair]):
    class Meta:
        model = TurnPair

    class Params:
        with_defence_card = False

    attack_card = CardFactory()
    defence_card = factory.Maybe(
        'with_defence_card',
        yes_declaration=CardFactory(),
    )


class TurnFactory(Factory[Turn]):
    class Meta:
        model = Turn

    pairs = factory.List([TurnPairFactory()])
