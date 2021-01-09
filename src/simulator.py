from collections import defaultdict

from blackjack import Actions, Deck, Player, Hand, play, resolve_environment

import numpy as np

### Policy for 6 deck, dealer hits on soft 17, surredender allowed,  

def stand():
    return Actions.STAND

def default_dict_stand():
    return defaultdict(stand)

hard_policy = defaultdict(default_dict_stand)

#hits 
for i in [4,5,6,7,8]:
    for j in range(2,11+1):
        hard_policy[i][j] = Actions.HIT

for j in [2] + [i for i in range(7,11+1)]:
    hard_policy[9][j] = Actions.HIT

for j in range(10,11+1):
    hard_policy[10][j] = Actions.HIT

for i in range(12,16+1):
    for j in range(7,11+1):
        hard_policy[i][j] = Actions.HIT

hard_policy[12][2] = Actions.HIT
hard_policy[12][3] = Actions.HIT

#doubles
for j in range(3,6+1):
    hard_policy[9][j] = Actions.DOUBLE_HIT

for j in range(2,9+1):
    hard_policy[10][j] = Actions.DOUBLE_HIT

for j in range(2,11+1):
    hard_policy[11][j] = Actions.DOUBLE_HIT


#Surredners
for i in range(15,16+1):
    for j in range(10,11+1):
        hard_policy[i][j] = Actions.SURRENDER_HIT
hard_policy[16][9] = Actions.SURRENDER_HIT
hard_policy[17][11] = Actions.SURRENDER_STAND

# Soft Policy 
soft_policy = defaultdict(default_dict_stand)
for i in range(13,17+1):
    for j in range(2,11+1):
        soft_policy[i][j] = Actions.HIT

for j in range(9,11+1):
    soft_policy[18][j] = Actions.HIT

for i in range(13,17+1):
    for j in range(5,6+1):
        soft_policy[i][j] = Actions.DOUBLE_HIT

for i in range(15, 17+1):
    soft_policy[i][4] = Actions.DOUBLE_HIT

soft_policy[17][3]=  Actions.DOUBLE_HIT

for j in range(2,6+1):
    soft_policy[18][j] = Actions.DOUBLE_STAND

soft_policy[19][6] = Actions.DOUBLE_STAND

# Split Policy
split_policy = defaultdict(default_dict_stand)
for i in range(2,11+1):
    for j in range(2,11+1):
        split_policy[i][j] = Actions.SPLIT

split_policy[5] = hard_policy[10].copy()
split_policy[10] = hard_policy[20].copy()

for i in range(2,7+1):
    for j in range(8,11+1):
        if i != 5: 
            split_policy[i][j] = Actions.HIT

for j in range(2,4+1):
    split_policy[4][j] = Actions.HIT

split_policy[4][7] = Actions.HIT
split_policy[6][7] = Actions.HIT

for j in range(5,6+1):
    split_policy[4][j] = Actions.SPLIT_IF_DOUBLE

for i in range(2,3+1):
    for j in range(2,3+1):
        split_policy[i][j] = Actions.SPLIT_IF_DOUBLE

split_policy[6][2] = Actions.SPLIT_IF_DOUBLE

#Stands
split_policy[9][7] = Actions.STAND
split_policy[9][10] = Actions.STAND
split_policy[9][11] = Actions.STAND


#surrenders
split_policy[8][11] = Actions.SURRENDER_SPLIT

# betting policy
wager_amts = [1,1,1,1,1,1,8,16,32]
ranges = [-3,-2,-1,0,0,1,2,3]
betting_policy = (wager_amts, ranges)

if __name__ == '__main__':
    results = []
    for i in range(10000):
        player = Player(bankroll=10000, hard_policy=hard_policy, soft_policy=soft_policy, split_policy=split_policy, betting_policy=betting_policy)
        deck = Deck(6)
        # need a way to get deck count
        resolve_environment(player, deck, 6, 3000, .35)
        results.append(player.bankroll)
    print('yo')    