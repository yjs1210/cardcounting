import pytest
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))
from blackjack import Deck, Hand, Cards, HandTypes


def test_hand_basic_functions():
    deck = Deck(99)
    hand = Hand([Cards.ACE, Cards.KING])
    hand_type, aces, lower_bound, upper_bound = hand.parse_hand()
    assert hand_type == HandTypes.SOFT
    assert lower_bound == 11
    assert upper_bound == 21

    hand.add_card(Cards.TWO)
    hand_type, aces, lower_bound, upper_bound = hand.parse_hand()
    assert hand_type == HandTypes.SOFT
    assert lower_bound == 13
    assert upper_bound == 23

    hand.delete_card(Cards.ACE)
    hand_type, aces, lower_bound, upper_bound = hand.parse_hand()
    assert hand_type == HandTypes.HARD
    assert lower_bound == 12
    assert upper_bound == 12

    hand = Hand([Cards.TWO, Cards.TWO])
    hand_type, aces, lower_bound, upper_bound = hand.parse_hand()
    assert hand_type == HandTypes.DUPLICATE
    assert lower_bound == 4
    assert upper_bound == 4

    hand.add_card(Cards.TWO)
    hand_type, aces, lower_bound, upper_bound = hand.parse_hand()
    assert hand_type == HandTypes.HARD
    assert lower_bound == 6
    assert upper_bound == 6

    hand = Hand([Cards.ACE, Cards.ACE])
    hand_type, aces, lower_bound, upper_bound = hand.parse_hand()
    assert hand_type == HandTypes.DUPLICATE
    assert lower_bound == 2
    assert upper_bound == 12


def test_setter_encapsulation():
    deck = Deck()
    with pytest.raises(AssertionError):
        deck.set_cards_left("51")
