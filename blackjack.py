import random

suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

deck = []

for suit in suits:
    for rank in ranks:
        deck.append(f'{rank} of {suit}')

random.shuffle(deck)

def deal_cards(deck, hand):

    card = deck.pop()
    hand.append(card) 

def calculate_hand_value(hand):
    value = 0
    has_ace = False

    for card in hand:
        rank = card.split()[0]

        if rank.isdigit():
            value += int(rank)
        elif rank in ['Jack', 'Queen', 'King']:
            value += 10
        elif rank == 'Ace':
            has_ace = True
            value += 11

    if has_ace and value > 21:
        value -= 10

    return value 

def play_blackjack():
    deck = []  # Reset the deck for a new game
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

    for suit in suits:
        for rank in ranks:
            deck.append(f'{rank} of {suit}')

    random.shuffle(deck)  # Shuffle the deck for a new game

    player_hand = []
    dealer_hand = []

    for _ in range(2):
        deal_cards(deck, player_hand)
        deal_cards(deck, dealer_hand)

    while True:
        yourHand = "Your hand" + str(player_hand) + " (" + str(calculate_hand_value(player_hand)) + ")\n"
        print(yourHand)
        dealerHand = "Dealer hand: [" + str(dealer_hand[0]) + ", <face down>]"
        print(dealerHand)

        if calculate_hand_value(player_hand) > 21:
            print('You bust! Game over.\n')
            return
        elif calculate_hand_value(player_hand) == 21:
            print('You win with a Blackjack!\n')
            return
        
        hitOrStand = "Hit or stand? (h/s)\n"
        print(hitOrStand)
        action = input()

        if action == 'h':
            deal_cards(deck, player_hand)
        elif action == 's':
            break
    
    dealerHand = "Dealer hand: " + str(dealer_hand)
   
    while calculate_hand_value(dealer_hand) < 17:
        deal_cards(deck, dealer_hand)

        dealerHand = "Dealer hand: " + str(dealer_hand) + " (" + str(calculate_hand_value(dealer_hand)) + ")\n"
        print(dealerHand)

    if calculate_hand_value(dealer_hand) > 21:
        print('Dealer busts! You win!\n')
    elif calculate_hand_value(player_hand) > calculate_hand_value(dealer_hand):
        print('You win!\n')
    elif calculate_hand_value(player_hand) < calculate_hand_value(dealer_hand):
        print('Dealer wins!\n')
    else:
        print('Tie!\n')


while True:
    play_blackjack()
    play_again = input('Do you want to play another game? (y/n)\n')
    if play_again.lower() != 'y' and play_again.lower() != 'yes':
        break
