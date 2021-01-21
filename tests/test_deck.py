import pytest
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))
from blackjack import Deck, Cards, Player
from simulator import soft_policy, split_policy, hard_policy


def test_deck_basic_functions():
    deck = Deck()
    assert deck.get_cards_left() == 52
    deck = Deck(2)
    assert deck.get_cards_left() == 52 * 2
    deck = Deck(6)
    assert deck.get_cards_left() == 52 * 6

    deck.deal()
    assert deck.get_cards_left() == 52 * 6 - 1


def test_card_count():
    deck = Deck()
    deck.set_cards(
        [
            Cards.TEN,
            Cards.QUEEN,
            Cards.KING,
            Cards.TEN,
            Cards.KING,
            Cards.ACE,
            Cards.TEN,
            Cards.QUEEN,
            Cards.QUEEN,
            Cards.JACK,
            Cards.TEN,
        ]
    )
    for i in range(11):
        deck.deal()
    assert deck.get_count() == -11

    cards = [
        Cards.FOUR,
        Cards.FIVE,
        Cards.SIX,
        Cards.SEVEN,
        Cards.EIGHT,
        Cards.TEN,
        Cards.ACE,
    ]
    deck = Deck()
    deck.set_cards(cards)
    for i in range(len(cards)):
        deck.deal()

    assert deck.get_count() == 1


def test_true_count_and_wager():
    wager_amts = [1, 1, 1, 1, 1, 1, 4, 8, 16]
    ranges = [-3, -2, -1, 0, 0, 1, 2, 3]
    betting_policy = (wager_amts, ranges)
    player = Player(
        bankroll=100,
        hard_policy=hard_policy,
        soft_policy=soft_policy,
        split_policy=split_policy,
        betting_policy=betting_policy,
    )
    deck = Deck()
    deck.set_cards(
        [
            Cards.TEN,
            Cards.QUEEN,
            Cards.KING,
            Cards.TEN,
            Cards.KING,
            Cards.ACE,
            Cards.TEN,
            Cards.QUEEN,
            Cards.QUEEN,
            Cards.JACK,
            Cards.TEN,
        ]
    )
    assert deck.get_num_decks() == 1
    assert deck.get_cards_left() == 11

    for i in range(10):
        deck.deal()

    assert deck.get_true_count() == -10 / (1 / 52)
    assert player.calculate_wager(deck.get_true_count()) == 1

    deck = Deck()
    deck.set_cards(
        [Cards.FOUR, Cards.TWO, Cards.SEVEN, Cards.TEN, Cards.NINE, Cards.TWO]
    )
    for i in range(5):
        deck.deal()
    assert deck.get_true_count() == 1 / (1 / 52)
    assert player.calculate_wager(deck.get_true_count()) == 16

    deck = Deck()
    deck.set_cards(
        [Cards.FOUR, Cards.TWO, Cards.SEVEN, Cards.TEN, Cards.NINE, Cards.TWO] * 100
    )
    for i in range(6 * 50):
        deck.deal()
    assert deck.get_true_count() == (2 * 50) / ((600 - 6 * 50) / 52)
    assert player.calculate_wager(deck.get_true_count()) == 16

    deck = Deck()
    deck.set_cards(
        [
            Cards.TWO,
            Cards.THREE,
            Cards.FOUR,
            Cards.FIVE,
            Cards.SIX,
            Cards.SEVEN,
            Cards.EIGHT,
            Cards.NINE,
            Cards.TEN,
            Cards.JACK,
            Cards.QUEEN,
            Cards.KING,
            Cards.ACE,
        ]
        * 100
    )
    for i in range(13 * 69):
        deck.deal()
    assert deck.get_true_count() == 0
    assert player.calculate_wager(deck.get_true_count()) == 1

    deck = Deck()
    deck.set_cards([Cards.FOUR, Cards.TWO, Cards.FOUR, Cards.FOUR] * 13)

    # +1
    deck.deal()
    assert deck.get_true_count() == 1 / (51 / 52)
    assert player.calculate_wager(deck.get_true_count()) == 4

    # +2
    deck.deal()
    assert deck.get_true_count() == 2 / (50 / 52)
    assert player.calculate_wager(deck.get_true_count()) == 8

    # +3
    deck.deal()
    assert deck.get_true_count() == 3 / (49 / 52)
    assert player.calculate_wager(deck.get_true_count()) == 16

    deck = Deck()
    deck.set_cards([Cards.QUEEN, Cards.JACK, Cards.ACE, Cards.TEN] * 13)
    wager_amts = [-16, -8, -4, -1, 0, 1, 4, 8, 16]
    ranges = [-3, -2, -1, 0, 0, 1, 2, 3]
    betting_policy_alt = (wager_amts, ranges)
    player = Player(
        bankroll=100,
        hard_policy=hard_policy,
        soft_policy=soft_policy,
        split_policy=split_policy,
        betting_policy=betting_policy_alt,
    )

    assert player.calculate_wager(deck.get_true_count()) == 0
    # +1
    deck.deal()
    assert deck.get_true_count() == -1 / (51 / 52)
    assert player.calculate_wager(deck.get_true_count()) == -4

    # +2
    deck.deal()
    assert deck.get_true_count() == -2 / (50 / 52)
    assert player.calculate_wager(deck.get_true_count()) == -8

    # +3
    deck.deal()
    assert deck.get_true_count() == -3 / (49 / 52)
    assert player.calculate_wager(deck.get_true_count()) == -16


def test_setter_encapsulation():
    deck = Deck()
    with pytest.raises(AssertionError):
        deck.set_cards_left("51")
