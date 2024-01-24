# Blackjack Minigame Chat Room
A chat server in Python, based on TCP, which also supports a blackjack minigame. 

The clients connect to the server and send requests and the server interprets them. If a GAME request is sent, the client that sent it will engage in a blackjack game, where the cards will be displayed. While the person is playing the game other clients on the server are able to chat together due to implemented multithreading. 
