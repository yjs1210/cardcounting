from typing import List, Set, Tuple, Dict
from collections import OrderedDict, defaultdict
import random
import bisect
import math
import copy
from multiprocessing import Pool

import ray
import numpy 
from aenum import Enum, NoAlias

class Cards(int, Enum, settings=NoAlias):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8 
    NINE = 9
    TEN = 10
    JACK = 10
    QUEEN = 10
    KING = 10
    ACE = 11 

class Suits(str, Enum):
    SPADES = "SPADES"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    CLUBS = "CLUBS"

class Actions(str, Enum):
    HIT = "HIT"
    STAND = "STAND"
    SPLIT = "SPLIT"
    SPLIT_IF_DOUBLE = "SPLIT_IF_DOUBLE"
    DOUBLE_STAND = "DOUBLE_STAND"
    DOUBLE_HIT = "DOUBLE_HIT"
    SURRENDER_HIT = "SURRENDER_HIT"
    SURRENDER_STAND = "SURRENDER_STAND"
    SURRENDER_SPLIT = "SURRENDER_SPLIT"
        
class HandTypes(str, Enum):
    DUPLICATE = "DUPLICATE"
    HARD = "HARD"
    SOFT = "SOFT"

class PlayerResultTypes(str, Enum):
    LIVE = "LIVE"
    BUST = "BUST"
    BLACKJACK = "BLACKJACK"
    SURRENDER = "SURRENDER"
    DOUBLE = "DOUBLE"

class DealerResultTypes(str, Enum):
    BLACKJACK = "BLACKJACK"
    BUST = "BUST"
    LIVE = "LIVE"

CARD_IDX = 0
SUIT_IDX = 1

RESULT_IDX = 0
VALUE_IDX = 1

WAGER_IDX = 0 
COUNT_RANGE_IDX = 1
class Deck():

    num_times_created = 0 

    def __init__(self, num_decks: int = 1, cards_in_a_deck = 52):
        assert isinstance(num_decks, int)
        if num_decks < 1:
            raise ValueError('Need to make at least one deck')

        cards = []
        for _ in range(num_decks):
            for _ in Suits:
                for card in Cards:
                        cards.append(card)
        
        n = len(cards)
        self.cards_left = n
        self.cards = cards
        self.count = 0
        self.num_decks = num_decks
        self.cards_in_a_deck = cards_in_a_deck
        self.shuffle()

    def deal(self):
        if len(self.get_cards()) == 0:
            return -1 
        else:
            new_card = self.get_cards().pop()
            self.cards_left -= 1
            self.count_card(new_card)
            return new_card

    def count_card(self, card):
        if card in [Cards.ACE, Cards.KING, Cards.QUEEN, Cards.JACK, Cards.TEN]:
            self.count -= 1
        if card in [Cards.TWO, Cards.THREE, Cards.FOUR, Cards.FIVE, Cards.SIX]:
            self.count += 1

    def shuffle(self):
        random.shuffle(self.get_cards())
    
    def check_threshhold(self, threshold):
        return (self.get_cards_left() / (self.get_cards_in_a_deck() * self.get_num_decks())) < threshold

    # getters
    def get_cards_left(self):
        return self.cards_left

    def get_cards(self):
        return self.cards

    def get_cards_in_a_deck(self):
        return self.cards_in_a_deck

    def get_count(self):
        return self.count
    
    def get_num_decks(self):
        return self.num_decks

    def get_true_count(self):
       return self.get_count() / (self.get_cards_left() / self.get_cards_in_a_deck())
        

    # setters
    def set_cards_left(self, num_cards: int):
        assert isinstance(num_cards, int)
        assert num_cards >= 0 
        self.cards_left = num_cards
    
    def set_cards(self, cards:List[Tuple['Cards','Suits']]):
        self.cards = cards 
        cards_left = len(cards)
        self.set_cards_left(cards_left)
        self.set_count(0)
        self.set_num_decks(math.ceil(cards_left/52))

    def set_count(self, count: int):
        assert isinstance(count, int)
        self.count = count
    
    def set_num_decks(self, num_decks: int):
        assert isinstance(num_decks, int)
        self.num_decks = num_decks


class Hand():

    def __init__(self, cards: List['Cards'], num_cards: int=2):
        self.cards = cards
        self.num_cards = num_cards    
    
    def add_card(self, card: 'Card'):
        self.cards += [card]
        self.set_num_cards(self.get_num_cards() + 1)

    def delete_card(self, card: 'Card'):
        self.cards.remove(card)
        self.set_num_cards(self.get_num_cards()- 1)
   
    def is_duplicate(self):
        return len(set(self.get_cards())) == 1 and self.get_num_cards() == 2

    def get_cards(self):
        return self.cards
    
    def get_num_cards(self):
        return self.num_cards

    def set_cards(self, cards: Set['Cards']):
        self.cards = cards    

    def set_num_cards(self, num_cards:int):
        assert isinstance(num_cards, int)
        assert num_cards > 0
        self.num_cards = num_cards 

    # returns number of aces, lower bound, upper bound
    def get_sum(self):
        lower_bound = 0
        upper_bound = 0 
        aces = 0 
        for card in self.cards:
            if card == Cards.ACE:
                aces += 1 
                lower_bound += 1
                upper_bound += 11 if aces == 1 else 1 
            else:
                lower_bound += card.value
                upper_bound += card.value

        return aces, lower_bound, upper_bound
    
    def parse_hand(self):
        aces, lower_bound, upper_bound = self.get_sum()

        if (self.get_num_cards() == 2) and self.is_duplicate():
            return HandTypes.DUPLICATE, aces, lower_bound, upper_bound
        if aces > 0:
            return HandTypes.SOFT, aces, lower_bound, upper_bound
        else:
            return HandTypes.HARD, aces, lower_bound, upper_bound


class Player():

    # when you implement more than 1 player, have a class variable bankroll and have 2 players

    def __init__(self, bankroll: int, hard_policy: Dict[int, Dict[int, 'Action']], soft_policy: Dict[int, Dict[int, 'Action']], split_policy: Dict[int, Dict[int, 'Action']], betting_policy: Tuple[List[int], List[int]], num_hands: int = 0 ):
        self.bankroll = bankroll
        self.hard_policy = hard_policy
        self.soft_policy = soft_policy
        self.split_policy = split_policy
        self.betting_policy = betting_policy
        self.num_hands = num_hands 

    def copy(self):
        return Player(bankroll=copy.copy(self.bankroll), hard_policy=copy.copy(self.hard_policy), soft_policy=copy.copy(self.soft_policy),  
        split_policy=copy.copy(self.split_policy), betting_policy=copy.copy(self.betting_policy),  num_hands=copy.copy(self.num_hands))


    def get_action(self, hand:'Hand', dealer_card: 'Card'):
        hand_type, aces, lower_bound, upper_bound= hand.parse_hand()
        value = lower_bound if upper_bound > 21 else upper_bound
        dealer_card_value = dealer_card.value 
        if hand_type == HandTypes.DUPLICATE and self.get_num_hands() < 4:
            if aces >0: 
                return self.split_policy[Cards.ACE.value][dealer_card_value], hand_type, aces, lower_bound, upper_bound
            return self.split_policy[upper_bound//2][dealer_card_value], hand_type, aces, lower_bound, upper_bound
        if hand_type == HandTypes.SOFT and lower_bound <=10:
            return self.soft_policy[value][dealer_card_value], hand_type, aces, lower_bound, upper_bound
        else:
            return self.hard_policy[value][dealer_card_value], hand_type, aces, lower_bound, upper_bound

    def increment_num_hands(self):
        self.num_hands += 1

    def next_round(self):
        self.num_hands = 0
    
    def get_num_hands(self):
        return self.num_hands
    
    def payout(self, num):
        self.bankroll += num
    
    def get_bankroll(self):
        return self.bankroll

    def calculate_wager(self, count):
        if count > 0:
            return self.betting_policy[WAGER_IDX][bisect.bisect(self.betting_policy[COUNT_RANGE_IDX], count)]
        if count < 0:
            return self.betting_policy[WAGER_IDX][bisect.bisect_left(self.betting_policy[COUNT_RANGE_IDX], count)]
        else:
            return self.betting_policy[WAGER_IDX][bisect.bisect(self.betting_policy[COUNT_RANGE_IDX], count) - 1] 
        
        

def resolve_player_action(hand:'Hand', dealer_card: 'Card', player:Player, deck):

    action, hand_type, aces, lower_bound, upper_bound = player.get_action(hand, dealer_card)
    num_cards = hand.get_num_cards()
    best_value =  upper_bound if upper_bound <= 21 else lower_bound

    if upper_bound > 21 and lower_bound > 21:
        return [(PlayerResultTypes.BUST, best_value)]
    if upper_bound == 21 and player.get_num_hands() == 1 and hand.get_num_cards() == 2: 
        return [(PlayerResultTypes.BLACKJACK, best_value)]
    if action == Actions.STAND or (action == Actions.DOUBLE_STAND and num_cards > 2) or (action == Actions.SURRENDER_STAND and num_cards > 2):
        return [(PlayerResultTypes.LIVE, best_value)]
    if action == Actions.HIT or (action == Actions.DOUBLE_HIT and num_cards > 2) or (action == Actions.SURRENDER_HIT and num_cards > 2):
        new_card = deck.deal()
        hand.add_card(new_card)
        return resolve_player_action(hand, dealer_card, player, deck)
    if action == Actions.SPLIT or action == Actions.SPLIT_IF_DOUBLE:
        player.increment_num_hands()
        card_1, card_2 = hand.get_cards()[0], hand.get_cards()[1]
        card_1_2= deck.deal()
        # deal with split aces
        if aces > 0 and (card_1_2 != Cards.ACE or player.get_num_hands() == 4) :
            new_value = card_1_2.value if card_1_2 != Cards.ACE else 1 
            result_1 = [(PlayerResultTypes.LIVE, Cards.ACE.value + new_value)]
        else:
            result_1 = resolve_player_action(Hand([card_1,card_1_2]), dealer_card, player, deck)

        card_2_2  = deck.deal()
        if aces > 0 and (card_2_2 != Cards.ACE or player.get_num_hands() == 4):
            new_value = card_2_2.value if card_2_2 != Cards.ACE else 1 
            result_2 = [(PlayerResultTypes.LIVE, Cards.ACE.value + new_value)]
        else:
            result_2 = resolve_player_action(Hand([card_2,card_2_2]), dealer_card, player, deck)
        
        return result_1 + result_2
    if action == Actions.DOUBLE_STAND or action == Actions.DOUBLE_HIT:
        new_card = deck.deal()
        if new_card == Cards.ACE:
            if aces > 0:
                new_upper = upper_bound + 1
                new_lower = lower_bound + 1
            else:
                new_upper = upper_bound + 11
                new_lower = lower_bound + 1
        else:
            new_upper = upper_bound + new_card.value 
            new_lower = lower_bound + new_card.value 
        value = new_upper if new_upper <= 21 else new_lower
        state = PlayerResultTypes.DOUBLE if value <= 21 else PlayerResultTypes.BUST
        return [(state, value)]
    
    if action == Actions.SURRENDER_HIT or action == Actions.SURRENDER_SPLIT or Actions.SURRENDER_STAND:
        return [(PlayerResultTypes.SURRENDER, best_value)]

def resolve_dealer_action(hand:'Hand', deck, num_cards = 2):
    aces, lower_bound, upper_bound = hand.get_sum()
    dealer_value = lower_bound if upper_bound > 21 else upper_bound
    if num_cards == 2 and dealer_value == 21:
        return (DealerResultTypes.BLACKJACK, 21)
    if dealer_value < 17 or (upper_bound == 17 and aces >0 and lower_bound < upper_bound):
        new_card = deck.deal()
        hand.add_card(new_card)
        return resolve_dealer_action(hand, deck, num_cards+1)    
    else:
        if dealer_value > 21:
            return (DealerResultTypes.BUST, dealer_value)
        else:
            return (DealerResultTypes.LIVE, dealer_value)

def check_if_new_deck(deck, threshold, num_decks):
    if deck.check_threshhold(threshold): 
        deck = Deck(num_decks)
        deck.shuffle()
        Deck.num_times_created += 1
    return deck     

def play(player, deck, wager=1):
       
    dealer_card_open, dealer_card_closed = deck.deal(), deck.deal()
    player_card1, player_card2 = deck.deal(), deck.deal()   
    player.increment_num_hands()
    dealer_blackjack = dealer_card_open.value + dealer_card_closed.value == 21
    player_blackjack =  player_card1.value + player_card2.value == 21

    if dealer_blackjack and not player_blackjack: 
        player.payout(-wager)
        return
    elif dealer_blackjack and player_blackjack:
        return 
    elif not dealer_blackjack and player_blackjack:
        player.payout(wager*1.5)
        return
    else:
        final_numbers = resolve_player_action(Hand([player_card1, player_card2]), dealer_card_open, player, deck)
        num_surrenders = 0
        num_busts = 0 
        live_hands = []
        num_hands = player.get_num_hands()
        for i in final_numbers:
            if i[RESULT_IDX]==PlayerResultTypes.SURRENDER:
                num_surrenders += 1
            elif i[RESULT_IDX]==PlayerResultTypes.BUST:
                num_busts += 1
            else:
                live_hands.append(i)
        
        if num_surrenders + num_busts > 0:
            player.payout(-(num_surrenders*1/2 + num_busts)*wager)
        
        # are there any live hands
        live_hands_n = num_hands - (num_surrenders + num_busts)
        if live_hands_n > 0:
            dealer_final = resolve_dealer_action(Hand([dealer_card_open, dealer_card_closed]), deck)
            for i in live_hands: 
                if i[RESULT_IDX] == PlayerResultTypes.LIVE:
                    if (i[VALUE_IDX] > dealer_final[VALUE_IDX]) or dealer_final[RESULT_IDX] == DealerResultTypes.BUST: 
                        player.payout(wager)
                    elif i[VALUE_IDX] == dealer_final[VALUE_IDX]:
                        continue
                    else:
                        player.payout(-wager)
                elif i[RESULT_IDX] == PlayerResultTypes.DOUBLE :
                    if (i[VALUE_IDX] > dealer_final[VALUE_IDX]) or dealer_final[RESULT_IDX] == DealerResultTypes.BUST:
                        player.payout(2*wager)
                    elif i[VALUE_IDX] == dealer_final[VALUE_IDX]:
                        continue
                    else:
                        player.payout(-2*wager)
                else:
                    raise Exception("There is a bug here")
        return 

def resolve_environment(player, starting_deck=None, num_decks = 6, iterations= 1000, threshold = .35):
    if not starting_deck:
        deck = Deck(num_decks)
        deck.shuffle()
    else:
        deck = starting_deck
    
    for i in range(iterations):
        true_count = deck.get_true_count()
        wager = player.calculate_wager(true_count)
        play(player=player, deck=deck, wager=wager)
        player.next_round()
        deck = check_if_new_deck(deck, threshold, num_decks)

def worker(num_decks, player, iterations, threshold):
    deck = Deck(num_decks)
    for i in range(iterations):
        true_count = deck.get_true_count()
        wager = player.calculate_wager(true_count)
        play(player=player, deck=deck, wager=wager)
        player.next_round()
        deck = check_if_new_deck(deck, threshold, num_decks)
    return player.get_bankroll()

def parallel_processing(player, num_decks = 6, iterations= 1000, n_samples = 100, threshold = .35, n_processes = 4):    
    pool = Pool()
    arguments = [(num_decks, player.copy(), iterations, threshold) for i in range(n_samples)]
    output = pool.starmap(worker, arguments)
    return output
        
if __name__ == '__main__':
    deck = Deck()
    deck.shuffle()
    dealer_card = deck.deal()
    player = Player()
    player_card1, player_card2 = deck.deal(), deck.deal()
    player_hand = Hand(set([player_card1,player_card2]))
    resolve_round(deck, player)

    