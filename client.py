import socket
import threading

# Constant declarations
CHAT_SERVER = ("127.0.0.1", 8043) # for testing

def bufferThread():
    buffer = ""
    while True:
        data = sock.recv(2)
        if data:
            buffer += data.decode("utf-8")
            if "\n" in buffer:
                response = buffer.split("\n")[0] + "\n"
                buffer = buffer.split("\n")[1]
                return response.encode("utf-8")

# Send a message to the server over the socket
def sendMessage(stringToSend):
    stringToSend = stringToSend.encode("utf-8")
    bytesTotal = len(stringToSend)
    bytesRemaining = bytesTotal

    while bytesRemaining > 0:
        bytesRemaining -= sock.send(stringToSend[bytesTotal-bytesRemaining:]) # sock.send() returns number of bytes that were sent

# Listen for messages from the server
def listenForMessages():
    try:
        while True:
            data = bufferThread()

            if data:
                # If the message contains data
                response = data.decode("utf-8")
                if "LIST-OK" in response:
                    print("Online users:")
                    onlineUsers = response.split()[1].split(',')
                    for user in onlineUsers:
                        print(user)
                elif "BAD-DEST-USER" in response:
                    print("Invalid recipient")
                elif "BAD-RQST-HDR" in response:
                    print("Invalid request header")
                elif "BAD-RQST-BODY" in response:
                    print("Invalid request body")
                elif "DELIVERY" in response:
                    sender = response.split()[1]
                    messageArray = response.split()
                    messageString = ""
                    for i in range(2, len(messageArray)):
                        # Concatenate the message array items into a string
                        messageString += messageArray[i] + " "
                    print("Message from " + sender + ": " + messageString)
                elif "GAME" in response:
                    # filter out the GAME and print everything else
                    print(response[4:])

    except:
        # Graceful exception handling
        return 0

# Login handling
loggedIn = False
while not loggedIn:
    # Attempt to connect to chat server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(CHAT_SERVER)
    username = input("Enter username: ")
    sendMessage("HELLO-FROM " + username + "\n")
    response = bufferThread().decode("utf-8")

    if response == "HELLO " + username + "\n":
        print("Logged in as " + username)
        loggedIn = True
    elif response == "IN-USE\n":
        print("Username already taken")
        sock.close()
    elif response == "BUSY\n":
        print("Server too busy")
        sock.close()
    elif response == "BAD-RQST-BODY\n":
        print("Bad username")
        sock.close()
    else:
        print("Unknown login error")
        sock.close()

# Confirm connected to chat server
print("Connected to chat server")

# Start the thread that listens for messages from the server to the user chat client
listeningThread = threading.Thread(target=listenForMessages, daemon=True)
listeningThread.start()

# Keep prompting the user for input until they enter "!quit"
while True:
    message = input()
    if message == "":
        print("Please enter a message")
    elif message == "!quit":
        break
    elif message == "!b":
        sendMessage("PLAY\n")
    elif message == "!who":
        sendMessage("LIST\n")
    elif message == "h":
        sendMessage("HIT\n")
    elif message == "s":
        sendMessage("STAND\n")
    elif message[0] == "@":
        # Handle message format "@username message"
        recipient = message[1:message.find(" ")]
        message = message[message.find(" "):]
        sendMessage("SEND " + recipient + " " + message + "\n")
    else:
        print("Invalid message")

# Disconnect from chat server
sock.close()

print("Disconnected from chat server")