import pytest

from durak.game.domain.exceptions import PlayerNotFoundError
from durak.game.domain.model.card import Card, Rank, Suit
from durak.game.domain.model.game import Game
from tests.factories.game.player import PlayerFactory


def _set_trump(game: Game, suit: Suit):
    # Make deck report the provided trump suit
    game.deck._trump_picked = True  # type: ignore[attr-defined]
    game.deck.cards = [Card(rank=Rank.SIX, suit=suit)]


def test_pick_defender_picks_first_defender():
    # Prepare a game with two players and a non-existent first_defender_id
    players = [PlayerFactory.build(), PlayerFactory.build()]
    game = Game(players=players, first_defender_id=players[0].id_)

    defender_id = game._pick_first_defender()

    assert defender_id == players[0].id_


def test_pick_defender_raises_when_first_defender_not_in_players():
    # Prepare a game with two players and a non-existent first_defender_id
    players = [PlayerFactory.build(), PlayerFactory.build()]
    game = Game(players=players, first_defender_id="non-existent-id")

    with pytest.raises(PlayerNotFoundError) as exc_info:
        game._pick_first_defender()

    assert exc_info.value.message == "Player with id %s not found" % "non-existent-id"


def test_pick_defender_selects_lowest_trump_holder_as_defender():
    # 3 players; the player with the lowest trump starts, the next one is the defender
    p0 = PlayerFactory.build()
    p1 = PlayerFactory.build()
    p2 = PlayerFactory.build()

    game = Game(players=[p0, p1, p2])
    _set_trump(game, Suit.HEARTS)

    # Hands: p0 -> HEARTS NINE, p1 -> HEARTS SEVEN (lowest trump), p2 -> HEARTS ACE
    p0.hand = [Card(rank=Rank.NINE, suit=Suit.HEARTS)]
    p1.hand = [Card(rank=Rank.SEVEN, suit=Suit.HEARTS)]
    p2.hand = [Card(rank=Rank.ACE, suit=Suit.HEARTS)]

    defender_id = game._pick_first_defender()

    # Expected: the lowest trump holder p1
    assert defender_id == p1.id_


def test_pick_defender_falls_back_to_first_player(monkeypatch):
    # No player has a trump card in hand; should use random.choice over player ids
    p0 = PlayerFactory.build()
    p1 = PlayerFactory.build()

    game = Game(players=[p0, p1])
    _set_trump(game, Suit.DIAMONDS)

    # Give non-trump cards only
    p0.hand = [Card(rank=Rank.ACE, suit=Suit.SPADES)]
    p1.hand = [Card(rank=Rank.KING, suit=Suit.CLUBS)]

    defender_id = game._pick_first_defender()

    assert defender_id == p0.id_
