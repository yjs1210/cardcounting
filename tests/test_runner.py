import pytest
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))
from simulator import hard_policy, soft_policy, split_policy, betting_policy
from blackjack import Actions, Cards, Deck, Player, resolve_player_action, Hand, PlayerResultTypes, resolve_dealer_action, DealerResultTypes, play, resolve_environment, parallel_processing
import numpy as np


def test_overall_play():
        
    wager_amts = [1,1,1,1,1,1,4,8,16]
    ranges = [-3,-2,-1,0,0,1,2,3]
    betting_policy = (wager_amts, ranges)

    player = Player(bankroll=100, hard_policy=hard_policy, soft_policy=soft_policy, split_policy=split_policy, betting_policy=betting_policy)
    deck = Deck()
    # first hand player wins and wins 1 count is now 4
    cards_1 = [Cards.TEN, Cards.THREE, Cards.TEN, Cards.FOUR, Cards.THREE , Cards.FOUR, Cards.TWO, Cards.FOUR]
    cards_2 = [Cards.TEN, Cards.THREE, Cards.TEN, Cards.FOUR, Cards.JACK , Cards.ACE, Cards.TEN, Cards.TEN]
    # second hand player wagers 16 and wins 16*1.5 = 24 
    deck.set_cards(cards_2 + cards_1)

    resolve_environment(player, deck, 8, 1, .001)
    assert player.get_bankroll() == 101
    assert deck.get_count() == 4
    assert player.calculate_wager(deck.get_true_count()) == 16
    resolve_environment(player, deck, 8, 1, .001)
    assert player.get_bankroll() == 125


def test_parallel():
    
    player = Player(bankroll=10000, hard_policy=hard_policy, soft_policy=soft_policy, split_policy=split_policy, betting_policy=betting_policy)
    output = parallel_processing(player=player, iterations=1000, n_samples=1000)
    stop_here

