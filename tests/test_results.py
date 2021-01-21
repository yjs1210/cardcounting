import pytest
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))
from simulator import hard_policy, soft_policy, split_policy, betting_policy
from blackjack import (
    Actions,
    Cards,
    Deck,
    Player,
    resolve_player_action,
    Hand,
    PlayerResultTypes,
    resolve_dealer_action,
    DealerResultTypes,
    play,
)

import numpy as np


def test_player_final_hands():
    # lots of splits, doesn't split more than 4
    deck = Deck()
    player = Player(
        bankroll=np.inf,
        hard_policy=hard_policy,
        soft_policy=soft_policy,
        split_policy=split_policy,
        betting_policy=betting_policy,
    )
    player.increment_num_hands()
    deck.set_cards(
        [
            Cards.TEN,
            Cards.QUEEN,
            Cards.KING,
            Cards.NINE,
            Cards.EIGHT,
            Cards.ACE,
            Cards.TEN,
            Cards.FOUR,
            Cards.EIGHT,
            Cards.NINE,
            Cards.TWO,
            Cards.TWO,
            Cards.TWO,
            Cards.TWO,
            Cards.TWO,
            Cards.TWO,
            Cards.TWO,
        ]
    )
    output = resolve_player_action(
        Hand([Cards.TWO, Cards.TWO]), Cards.SEVEN, player, deck
    )
    assert output == [
        (PlayerResultTypes.LIVE, 21),
        (PlayerResultTypes.DOUBLE, 14),
        (PlayerResultTypes.LIVE, 21),
        (PlayerResultTypes.DOUBLE, 21),
    ]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards(
        [
            Cards.FIVE,
            Cards.FIVE,
            Cards.TWO,
            Cards.KING,
            Cards.ACE,
            Cards.ACE,
            Cards.ACE,
            Cards.ACE,
        ]
    )
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.ACE]), Cards.SEVEN, player, deck
    )
    assert output == [
        (PlayerResultTypes.LIVE, 12),
        (PlayerResultTypes.LIVE, 12),
        (PlayerResultTypes.LIVE, 21),
        (PlayerResultTypes.LIVE, 13),
    ]

    player.next_round()
    player.increment_num_hands()
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.JACK]), Cards.SEVEN, player, deck
    )
    assert output == [(PlayerResultTypes.BLACKJACK, 21)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards(
        [
            Cards.FIVE,
            Cards.FIVE,
            Cards.TWO,
            Cards.KING,
            Cards.ACE,
            Cards.ACE,
            Cards.ACE,
            Cards.ACE,
        ]
    )
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.SIX]), Cards.SIX, player, deck
    )
    assert output == [(PlayerResultTypes.DOUBLE, 18)]

    player.next_round()
    player.increment_num_hands()
    output = resolve_player_action(
        Hand([Cards.JACK, Cards.SIX]), Cards.ACE, player, deck
    )
    assert output == [(PlayerResultTypes.SURRENDER, 16)]

    player.next_round()
    player.increment_num_hands()
    output = resolve_player_action(
        Hand([Cards.JACK, Cards.SEVEN]), Cards.ACE, player, deck
    )
    assert output == [(PlayerResultTypes.SURRENDER, 17)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.TEN, Cards.THREE])
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.TWO]), Cards.TWO, player, deck
    )
    assert output == [(PlayerResultTypes.LIVE, 16)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.SIX, Cards.TEN, Cards.THREE])
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.TWO]), Cards.SEVEN, player, deck
    )
    assert output == [(PlayerResultTypes.BUST, 22)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.THREE])
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.SEVEN]), Cards.TWO, player, deck
    )
    assert output == [(PlayerResultTypes.DOUBLE, 21)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.FIVE])
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.SEVEN]), Cards.TWO, player, deck
    )
    assert output == [(PlayerResultTypes.DOUBLE, 13)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.FIVE])
    output = resolve_player_action(
        Hand([Cards.ACE, Cards.EIGHT]), Cards.TWO, player, deck
    )
    assert output == [(PlayerResultTypes.LIVE, 19)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.FIVE])
    output = resolve_player_action(
        Hand([Cards.NINE, Cards.NINE]), Cards.SEVEN, player, deck
    )
    assert output == [(PlayerResultTypes.LIVE, 18)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.FIVE])
    output = resolve_player_action(
        Hand([Cards.EIGHT, Cards.EIGHT]), Cards.ACE, player, deck
    )
    assert output == [(PlayerResultTypes.SURRENDER, 16)]

    player.next_round()
    player.increment_num_hands()
    deck.set_cards([Cards.FIVE])
    output = resolve_player_action(
        Hand([Cards.TEN, Cards.TEN]), Cards.ACE, player, deck
    )
    assert output == [(PlayerResultTypes.LIVE, 20)]


def test_dealer_final_hands():
    deck = Deck()
    deck.set_cards(
        [
            Cards.SIX,
            Cards.FOUR,
            Cards.ACE,
            Cards.THREE,
            Cards.TEN,
            Cards.TWO,
            Cards.TWO,
            Cards.FOUR,
            Cards.TWO,
            Cards.TWO,
            Cards.THREE,
            Cards.TEN,
            Cards.FIVE,
            Cards.TEN,
        ]
    )
    assert resolve_dealer_action(Hand([Cards.ACE, Cards.JACK]), deck) == (
        DealerResultTypes.BLACKJACK,
        21,
    )
    assert resolve_dealer_action(Hand([Cards.ACE, Cards.SIX]), deck) == (
        DealerResultTypes.LIVE,
        17,
    )
    assert resolve_dealer_action(Hand([Cards.TEN, Cards.SIX]), deck) == (
        DealerResultTypes.LIVE,
        21,
    )
    assert resolve_dealer_action(Hand([Cards.TEN, Cards.TWO]), deck) == (
        DealerResultTypes.BUST,
        22,
    )
    assert resolve_dealer_action(Hand([Cards.FIVE, Cards.THREE]), deck) == (
        DealerResultTypes.LIVE,
        19,
    )
    assert resolve_dealer_action(Hand([Cards.ACE, Cards.ACE]), deck) == (
        DealerResultTypes.LIVE,
        19,
    )
    assert resolve_dealer_action(Hand([Cards.TWO, Cards.FOUR]), deck) == (
        DealerResultTypes.LIVE,
        21,
    )
    assert resolve_dealer_action(Hand([Cards.TEN, Cards.SIX]), deck) == (
        DealerResultTypes.BUST,
        22,
    )


def test_play():
    player = Player(
        bankroll=100,
        hard_policy=hard_policy,
        soft_policy=soft_policy,
        split_policy=split_policy,
        betting_policy=betting_policy,
    )
    deck = Deck(99)
    # blackjacks
    hands_1 = [
        Cards.ACE,
        Cards.JACK,
        Cards.TWO,
        Cards.FOUR,
    ]  # player black jack dealer no blackjack
    hands_2 = [
        Cards.ACE,
        Cards.JACK,
        Cards.ACE,
        Cards.JACK,
    ]  # player black jack dealer blackjack
    hands_3 = [
        Cards.FOUR,
        Cards.TWO,
        Cards.ACE,
        Cards.JACK,
    ]  # player no black jack dealer blackjack
    # hits
    hands_4 = [
        Cards.TEN,
        Cards.EIGHT,
        Cards.TWO,
        Cards.TEN,
        Cards.TEN,
    ]  # Dealer shows T, has another T, Player hits with 10 to get to 20, push
    hands_5 = [
        Cards.TEN,
        Cards.TEN,
        Cards.EIGHT,
        Cards.TWO,
        Cards.TWO,
        Cards.TEN,
    ]  # Dealer shows T, has a Two, Player hits with 10 to get to 20, dealer busts to 22
    hands_6 = [
        Cards.SEVEN,
        Cards.EIGHT,
        Cards.TWO,
        Cards.TEN,
        Cards.TEN,
    ]  # Dealer shows T, has a another T, Player hits with 10 to get to 17, stands and lose
    hands_7 = [Cards.SEVEN, Cards.EIGHT, Cards.TEN, Cards.TEN]  # Surrender 15
    hands_8 = [
        Cards.TEN,
        Cards.THREE,
        Cards.TEN,
        Cards.TWO,
        Cards.JACK,
        Cards.TWO,
    ]  # Dealer Shows two, player has 12, player hits and stands at 15, dealer  hits and busts at 22
    hands_9 = [
        Cards.FIVE,
        Cards.THREE,
        Cards.TEN,
        Cards.TWO,
        Cards.JACK,
        Cards.TWO,
    ]  # Dealer Shows two, player has 12, player hits and stands at 15, dealer  hits and wins busts at 17

    # player stands
    hands_10 = [
        Cards.FIVE,
        Cards.THREE,
        Cards.TEN,
        Cards.THREE,
        Cards.JACK,
        Cards.TWO,
    ]  # Dealer Shows two, player has 13 and stands, dealer wins with 20
    hands_11 = [
        Cards.TEN,
        Cards.SEVEN,
        Cards.JACK,
        Cards.JACK,
    ]  # Player has 17 stands and loses
    hands_12 = [
        Cards.TEN,
        Cards.TEN,
        Cards.JACK,
        Cards.NINE,
    ]  # Player has 20 stands and wins

    # regular surredners
    hands_13 = [
        Cards.FIVE,
        Cards.TEN,
        Cards.JACK,
        Cards.TEN,
    ]  # Player has 15 surrenders to 10 and loses
    hands_14 = [
        Cards.FIVE,
        Cards.TEN,
        Cards.NINE,
        Cards.ACE,
    ]  # Player has 15 surrenders to 11 and loses
    hands_15 = [
        Cards.SIX,
        Cards.TEN,
        Cards.JACK,
        Cards.NINE,
    ]  # Player has 16 surrenders to 9 and loses
    hands_16 = [
        Cards.SIX,
        Cards.TEN,
        Cards.JACK,
        Cards.KING,
    ]  # Player has 16 surrenders to 10 and loses
    hands_17 = [
        Cards.SIX,
        Cards.TEN,
        Cards.SEVEN,
        Cards.ACE,
    ]  # Player has 16 surrenders to A and loses
    hands_18 = [
        Cards.SEVEN,
        Cards.TEN,
        Cards.SEVEN,
        Cards.ACE,
    ]  # Player has 17 surrenders to A and loses
    hands_19 = [
        Cards.FIVE,
        Cards.TEN,
        Cards.JACK,
        Cards.ACE,
    ]  # Player has opportunity to surrender but blackjack overrules and dealer wins

    # regular splits, max 4
    hands_20 = [
        Cards.SEVEN,
        Cards.TEN,
        Cards.JACK,
        Cards.TEN,
        Cards.EIGHT,
        Cards.SEVEN,
        Cards.ACE,
        Cards.EIGHT,
        Cards.TWO,
        Cards.TWO,
        Cards.TWO,
        Cards.TWO,
        Cards.TEN,
        Cards.SEVEN,
    ]  # split twos 4 times. DOuble the first, Win with 21, Second to 9 does not double. Hits to 17 to push, Third bust at 22, Fourth stays at 19 to win.
    hands_21 = [
        Cards.TEN,
        Cards.TEN,
        Cards.FIVE,
        Cards.ACE,
        Cards.ACE,
        Cards.SEVEN,
        Cards.FOUR,
        Cards.FOUR,
        Cards.FOUR,
        Cards.TWO,
        Cards.SIX,
    ]  # Split 4 three times, doubles to 12 to lose, Doubles to 20 to win, Stays at 14 to lose
    hands_22 = [
        Cards.EIGHT,
        Cards.THREE,
        Cards.TWO,
        Cards.TEN,
        Cards.ACE,
        Cards.ACE,
        Cards.ACE,
        Cards.ACE,
        Cards.NINE,
        Cards.ACE,
    ]  # Split Aces 4 times, Win first, lose all three others

    # soft hands
    hands_23 = [
        Cards.SIX,
        Cards.THREE,
        Cards.TWO,
        Cards.ACE,
        Cards.TEN,
        Cards.SIX,
    ]  # Doubles Ace and wins to a dealer bust
    hands_24 = [
        Cards.FIVE,
        Cards.TEN,
        Cards.TWO,
        Cards.ACE,
        Cards.TEN,
        Cards.SIX,
    ]  # Doubles Ace to 13 and and loses to dealer 21
    hands_25 = [
        Cards.ACE,
        Cards.SEVEN,
        Cards.ACE,
        Cards.SEVEN,
        Cards.TEN,
    ]  # Hits soft 18 vs ten and wins with 18 to 17
    hands_26 = [
        Cards.ACE,
        Cards.SEVEN,
        Cards.ACE,
        Cards.TEN,
        Cards.TEN,
    ]  # Hits soft 18 vs ten and loses with 18 to 20
    hands_27 = [
        Cards.FOUR,
        Cards.SIX,
        Cards.ACE,
        Cards.TEN,
        Cards.TEN,
    ]  # Hits soft 17 and stays at 21 and wins
    hands_28 = [
        Cards.NINE,
        Cards.NINE,
        Cards.SIX,
        Cards.ACE,
        Cards.TEN,
        Cards.TEN,
    ]  # Hits soft 17 and busts
    hands_29 = [
        Cards.SEVEN,
        Cards.THREE,
        Cards.FOUR,
        Cards.TWO,
        Cards.ACE,
        Cards.TEN,
        Cards.THREE,
    ]  # Hits soft 13, gets to soft 17 vs 3, can't double and push at 20
    hands_30 = [
        Cards.TEN,
        Cards.FIVE,
        Cards.SEVEN,
        Cards.ACE,
        Cards.TEN,
        Cards.TWO,
    ]  # Doubles 18 vs 2 wins to bust

    # hits many cards into doubles, doesn't double and wins
    deck.set_cards(
        deck.get_cards()
        + hands_30
        + hands_29
        + hands_28
        + hands_27
        + hands_26
        + hands_25
        + hands_24
        + hands_23
        + hands_22
        + hands_21
        + hands_20
        + hands_19
        + hands_18
        + hands_17
        + hands_16
        + hands_15
        + hands_14
        + hands_13
        + hands_12
        + hands_11
        + hands_10
        + hands_9
        + hands_8
        + hands_7
        + hands_6
        + hands_5
        + hands_4
        + hands_3
        + hands_2
        + hands_1
    )

    # test blackjacks
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (1 * 1.5)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (1 * 1.5)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (0.5)

    # test regular hits
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (0.5)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (1 * 1.5)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (1 * 0.5)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100

    # test regular stands
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 99
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 98
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 99

    # test regular surrenders
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 98.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 98
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 97.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 97
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 96.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 96
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 95

    # test regular splits
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (95 + 2 + 0 - 1 + 1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (97 - 2 + 2 - 1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (96 + 1 - 3)

    # test soft hands
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (94 + 2)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (96 - 2)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (94 + 1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (95 - 1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (94 + 1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (95 - 1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (94)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == (94 + 2)


def test_play_set2():
    player = Player(
        bankroll=100,
        hard_policy=hard_policy,
        soft_policy=soft_policy,
        split_policy=split_policy,
        betting_policy=betting_policy,
    )
    deck = Deck(99)
    hands_1 = [Cards.TEN, Cards.FIVE, Cards.SEVEN, Cards.ACE, Cards.TEN, Cards.TWO]
    # test stand with dupl;icate hands
    hands_1 = [Cards.NINE, Cards.NINE, Cards.TEN, Cards.SEVEN]
    hands_2 = [Cards.NINE, Cards.NINE, Cards.NINE, Cards.ACE]
    hands_3 = [Cards.NINE, Cards.NINE, Cards.TEN, Cards.QUEEN]

    # test hits with duplicate hands
    hands_4 = [Cards.TEN, Cards.SEVEN, Cards.TWO, Cards.TWO, Cards.TEN, Cards.QUEEN]
    hands_5 = [Cards.TEN, Cards.FOUR, Cards.FOUR, Cards.TEN, Cards.QUEEN]

    # test surredern with 8,8
    hands_6 = [Cards.EIGHT, Cards.EIGHT, Cards.NINE, Cards.ACE]

    # test softs hits into soft 16-18 but does not double
    hands_7 = [
        Cards.SEVEN,
        Cards.FIVE,
        Cards.TWO,
        Cards.ACE,
        Cards.NINE,
        Cards.TWO,
    ]  # becomes, soft 18, stands since you can't double with 3 cards, push
    hands_8 = [
        Cards.EIGHT,
        Cards.SIX,
        Cards.FOUR,
        Cards.TWO,
        Cards.ACE,
        Cards.NINE,
        Cards.THREE,
    ]  # becomes, hard 13, stands and loses
    hands_9 = [
        Cards.NINE,
        Cards.NINE,
        Cards.FIVE,
        Cards.FOUR,
        Cards.TWO,
        Cards.ACE,
        Cards.NINE,
        Cards.THREE,
    ]  # becomes, hard 12 hits, makes 21 push

    # test bunch of weird surredner hit surredner stand,... etc rules
    hands_10 = [
        Cards.TEN,
        Cards.EIGHT,
        Cards.FOUR,
        Cards.FOUR,
        Cards.NINE,
        Cards.ACE,
    ]  # does not split 44, hits into 16, but doesn't surrender, busts.
    hands_11 = [Cards.TEN, Cards.SEVEN, Cards.NINE, Cards.ACE]  # surrender 17
    hands_12 = [
        Cards.TEN,
        Cards.SEVEN,
        Cards.TEN,
        Cards.ACE,
    ]  # dealer BJ can't surrender
    hands_13 = [
        Cards.FIVE,
        Cards.TEN,
        Cards.TWO,
        Cards.NINE,
        Cards.ACE,
    ]  # hits into surrender can't surrender, stands

    deck.set_cards(
        deck.get_cards()
        + hands_13
        + hands_12
        + hands_11
        + hands_10
        + hands_9
        + hands_8
        + hands_7
        + hands_6
        + hands_5
        + hands_4
        + hands_3
        + hands_2
        + hands_1
    )
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 + (1)
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 101 - 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 - 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 99 + 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 100 - 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 99 - 0.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 98.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 98.5 - 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 97.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 97.5 - 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 96.5 - 0.5
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 96 - 1
    plays = play(player, deck=deck, wager=1)
    player.next_round()
    assert player.get_bankroll() == 95 - 1
    print("yo?")
