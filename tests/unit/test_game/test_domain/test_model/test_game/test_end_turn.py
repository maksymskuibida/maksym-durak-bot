from durak.game.domain.constants import HAND_SIZE
from durak.game.domain.model.deck import Deck
from durak.game.domain.model.game import Game, GameStatus
from durak.game.domain.model.player import PlayerStatus
from tests.factories.game.card import CardFactory
from tests.factories.game.game import GameFactory
from tests.factories.game.player import PlayerFactory


def test_deal_cards_after_turn():
    game = GameFactory.build()

    for player in game.players:
        assert len(player.hand) == 0

    game._deal_cards_after_turn()

    for player in game.players:
        assert len(player.hand) == HAND_SIZE


def test_id_doesnt_raise_if_deck_is_empty():
    game = GameFactory.build(deck=Deck(cards=[]))

    for player in game.players:
        assert len(player.hand) == 0

    game._deal_cards_after_turn()

    for player in game.players:
        assert len(player.hand) == 0


def test_set_empty_handed_players_to_finish():
    game = GameFactory.build(
        players__0__hand=[CardFactory.build()], deck=Deck(cards=[])
    )

    assert game.deck.is_empty
    assert len(game.players) == 2
    assert not game.players[0].is_empty_hand
    assert game.players[1].is_empty_hand

    game._set_empty_handed_players_to_finish()

    assert game.players[0].is_in_game
    assert not game.players[1].is_in_game


def test_rotate_defender_moves_to_next_active_no_wrap(get_players):
    # 4 players: p0, p1 (defender), p2, p3 — all in game
    players = get_players(4)
    game = Game(players=players)
    game.defender_id = players[1].id_

    game._rotate_defender()

    assert game.defender_id == players[2].id_


ess_case_doc = """The defender should rotate to the next player to the right
skipping any players that are not in game (FINISHED or LOST)."""


def test_rotate_defender_skips_inactive_players(get_players):
    # 4 players: p0 (defender), p1 FINISHED, p2 FINISHED, p3 in game
    players = get_players(4)
    game = Game(players=players)

    game.defender_id = players[0].id_
    players[1].set_status(PlayerStatus.FINISHED)
    players[2].set_status(PlayerStatus.FINISHED)

    game._rotate_defender()

    assert game.defender_id == players[3].id_


def test_rotate_defender_wraps_to_start_when_defender_is_last(get_players):
    # 4 players: p0, p1, p2, p3 (defender). Next should be p0
    players = get_players(4)
    game = Game(players=players)
    game.defender_id = players[3].id_

    game._rotate_defender()

    assert game.defender_id == players[0].id_


def test_rotate_defender_wraps_and_skips_inactive_at_start(get_players):
    # 5 players: p0 FINISHED, p1 in game, p2 in game, p3 in game, p4 defender
    # Expected next defender: p1 (wrap to start, skip p0)
    players = get_players(5)
    game = Game(players=players)

    players[0].set_status(PlayerStatus.FINISHED)
    game.defender_id = players[4].id_

    game._rotate_defender()

    assert game.defender_id == players[1].id_


def test_finish():
    game = GameFactory.build()
    game.start()

    game.players[0].set_status(PlayerStatus.FINISHED)

    assert len(game.active_players) == 1
    assert game.status == GameStatus.IN_PROGRESS

    game._finish()

    assert len(game.active_players) == 0
    assert game.players[0].status == PlayerStatus.FINISHED
    assert game.players[1].status == PlayerStatus.LOST
    assert game.status == GameStatus.FINISHED


def test_end_turn(get_players):
    # Initialize data
    players = get_players(3)
    game = GameFactory.build(players=players, first_defender_id=players[0].id_)
    game.start()
    game.deck.cards = [game.deck.cards[0]]

    # remove the last card from the first player's hand
    game.players[0].hand.pop()

    # clear the second player's hand
    game.players[1].hand.clear()

    # cut the third player's cards to 4
    game.players[2].hand = game.players[2].hand[:4]

    # verify lengths are as expected
    assert len(game.players[0].hand) == 5
    assert len(game.players[1].hand) == 0
    assert len(game.players[2].hand) == 4

    game._end_turn()

    # verify the game wasn't finished
    assert game.status == GameStatus.IN_PROGRESS

    # verify defender is set to the third player, as the second one is finished
    assert game.defender.id_ == players[2].id_

    # verify the first player is still in the game
    assert game.players[0].status == PlayerStatus.IN_GAME
    # verify the first player received the last card from deck
    assert len(game.players[0].hand) == 6

    # verify the second player is finished
    assert game.players[1].status == PlayerStatus.FINISHED
    # verify the second player's hand is empty
    assert len(game.players[1].hand) == 0

    # verify the third player is still in the game
    assert game.players[2].status == PlayerStatus.IN_GAME
    # verify the third player didn't receive a new card, as the deck had only one card left
    assert len(game.players[2].hand) == 4


def test_end_turn_finished_the_game_if_one_player_left(get_players):
    # Initialize data
    players = get_players(2)
    game = GameFactory.build(players=players, first_defender_id=players[0].id_)
    game.start()
    game.deck.cards = [game.deck.cards[0]]

    # remove the last card from the first player's hand
    game.players[0].hand.pop()

    # clear the second player's hand
    game.players[1].hand.clear()

    # verify lengths are as expected
    assert len(game.players[0].hand) == 5
    assert len(game.players[1].hand) == 0

    defender_id_before = game.defender.id_

    game._end_turn()

    # verify the game wasn't finished
    assert game.status == GameStatus.FINISHED
    assert game.defender_id == defender_id_before

    # verify the first player is lost
    assert game.players[0].status == PlayerStatus.LOST
    # verify the first player received the last card from deck
    assert len(game.players[0].hand) == 6

    # verify the second player is finished
    assert game.players[1].status == PlayerStatus.FINISHED
    # verify the second player's hand is empty
    assert len(game.players[1].hand) == 0
