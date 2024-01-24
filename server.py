import socket
import threading
import random
 
# Constant declarations
CHAT_SERVER = ("127.0.0.1", 8043)
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

# Global variables
usersLoggedIn = [] # Format: [username, [[message, from], ...] ]
serverBusy = False # Set true to decline new login requests
maxUsers = 64 # Maximum number of users that can be logged in at once
currentUser = None
deck = []

# Listen on the specified address and port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(CHAT_SERVER)
server.listen()

for suit in suits:
    for rank in ranks:
        deck.append(f'{rank} of {suit}')

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

def send_message_to_client(message, user):
    response = ("GAME" + message + "\n").encode("utf-8")
    user.send(response)

def play_blackjack():
    global currentUser

    if currentUser != None:
        send_message_to_client("You are already playing a game!", currentUser)
        return
    else :
        currentUser = client

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
        yourHand = "Your hand" + str(player_hand) + " (" + str(calculate_hand_value(player_hand)) + ")"
        send_message_to_client(yourHand, currentUser)
        dealerHand = "Dealer hand: [" + str(dealer_hand[0]) + ", <face down>]"
        send_message_to_client(dealerHand, currentUser)

        if calculate_hand_value(player_hand) > 21:
            send_message_to_client('You bust! Game over.', currentUser)
            return
        elif calculate_hand_value(player_hand) == 21:
            send_message_to_client('You win with a Blackjack!', currentUser)
            return
        
        hitOrStand = "Hit or stand? (h/s)"
        send_message_to_client(hitOrStand, currentUser)
        action = client.recv(1024).decode("utf-8")

        if "HIT" in action:
            deal_cards(deck, player_hand)
        else :
            break
    
    dealerHand = "Dealer hand: " + str(dealer_hand) + " (" + str(calculate_hand_value(dealer_hand)) + ")"
    send_message_to_client(dealerHand, currentUser)
   
    while calculate_hand_value(dealer_hand) < 17:
        deal_cards(deck, dealer_hand)

        dealerHand = "Dealer hand: " + str(dealer_hand) + " (" + str(calculate_hand_value(dealer_hand)) + ")"
        send_message_to_client(dealerHand, currentUser)

    if calculate_hand_value(dealer_hand) > 21:
            send_message_to_client('Dealer busts! You win!', currentUser)
    elif calculate_hand_value(player_hand) > calculate_hand_value(dealer_hand):
        send_message_to_client('You win!', currentUser)
    elif calculate_hand_value(player_hand) < calculate_hand_value(dealer_hand):
        send_message_to_client('Dealer wins!', currentUser)
    else:
        send_message_to_client('Tie!', currentUser)

    currentUser = None

def bufferThread(client):
    buffer = ""
    while True:
        data = client.recv(1024)  # Use a larger buffer size
        if not data:
            break  # Exit the loop if the client disconnects
        buffer += data.decode("utf-8")
        
        while "\n" in buffer:
            message, _, buffer = buffer.partition("\n")
            return message.encode("utf-8")
        
# The thread which checks if the logged in user has any messages in their "mailbox" in usersLoggedIn[1] array
def messageReceived(client, username):
    while True:
        for user in usersLoggedIn:
            # Iterate through all logged in users
            if user[0] == username:
                # For the user that is logged in
                if user[1]:
                    # If they have any messages in their mailbox
                    messageObject = user[1].pop()
                    message = messageObject[0]
                    sender = messageObject[1]
                    response = ("DELIVERY " + sender + " " + message + "\n").encode("utf-8")
                    client.send(response)
                    print("Sent: " + response.decode("utf-8"))
                break
    
# Server logic for handing requests from clients
def handleClientRequests(client, address):
    username = None
    loggedIn = False

    # Confirm when client connected
    print("Client connected: " + str(address) + "\n")

    while True:
        try:
            data = bufferThread(client)

            if data:
                request = data.decode("utf-8")
                print("Request: " + request)

                if loggedIn:
                    if "LIST" in request:
                        response = ("LIST-OK " + ",".join([user[0] for user in usersLoggedIn]) + "\n").encode("utf-8")
                        client.send(response)
                        print("Response: " + response.decode("utf-8"))
                    elif "SEND" in request:
                        recipient = request.split()[1]
                        messageArray = request.split()
                        messageString = ""
                        for i in range(2, len(messageArray)):
                            messageString += messageArray[i] + " "
                        if recipient and messageString:
                            recipient_found = False
                            for user in usersLoggedIn:
                                if user[0] == recipient:
                                    user[1].append([messageString, username])
                                    response = ("SEND-OK " + recipient + " " + messageString + "\n").encode("utf-8")
                                    client.send(response)
                                    print("Response: " + response.decode("utf-8"))
                                    recipient_found = True
                                    break
                            if not recipient_found:  
                                response = ("BAD-DEST-USER" + "\n").encode("utf-8")
                                client.send(response)
                                print("Response: " + response.decode("utf-8"))
                                
                        else:
                            response = ("BAD-RQST-BODY" + "\n").encode("utf-8")
                            client.send(response)
                            print("Response: " + response.decode("utf-8"))
                    elif "PLAY" in request:
                        play_blackjack()
                    elif "POO" in request:
                        client.send("POO".encode("utf-8"))
                else:
                    # Not logged in yet
                    if "HELLO-FROM" in request:
                        if len(usersLoggedIn) < maxUsers:
                            serverBusy = False
                        else:
                            serverBusy = True
                        if not serverBusy:
                            # Server is accepting new login requests
                            username = request.split()[1]
                            if username:
                                # If the username is not empty
                                usernameTaken = False
                                for user in usersLoggedIn:
                                    if user[0] == username:
                                        usernameTaken = True
                                        break
                                if not usernameTaken and username != "!who" and username != "!send" and username != "!quit":
                                    # Username is not taken
                                    userObject = [username, []] # Format: [username, [[message, from], ...] ]
                                    usersLoggedIn.append(userObject)
                                    loggedIn = True
                                    response = ("HELLO " + username + "\n").encode("utf-8")
                                    client.send(response)
                                    print("Response: " + response.decode("utf-8"))

                                    # Start a new thread to handle when this user gets messages in their "mailbox"
                                    threading.Thread(target=messageReceived, args=(client, username)).start()
                                else:
                                    # Username is already taken
                                    response = ("IN-USE" + "\n").encode("utf-8")
                                    client.send(response)
                                    print("Response: " + response.decode("utf-8"))
                            else:
                                # Username is empty
                                response = ("BAD-RQST-BODY" + "\n").encode("utf-8")
                                client.send(response)
                                print("Response: " + response.decode("utf-8"))
                        else:
                            # Server is not accepting new login requests (serverBusy = True)
                            response = ("BUSY" + "\n").encode("utf-8")
                            client.send(response)
                            print("Response: " + response.decode("utf-8"))
                    else:
                        # Request header is invalid
                        response = ("BAD-RQST-HDR" + "\n").encode("utf-8")
                        client.send(response)
                        print("Response: " + response.decode("utf-8"))
        except ConnectionResetError:
            # If the client closes the connection to the server
            for user in usersLoggedIn:
                # Find the user in the usersLoggedIn array
                if user[0] == username:
                    # Remove them from it
                    usersLoggedIn.remove(user)
                    break
            print("Client disconnected: " + str(address) + ", username: " + username + "\n")
    
while True:
    # Accept new connections
    client, address = server.accept()
    
    # Start a new thread to handle each client's requests
    threading.Thread(target=handleClientRequests, args=(client, address)).start()
    