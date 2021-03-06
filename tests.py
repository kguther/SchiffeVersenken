#!/usr/bin/python           # This is client.py file
import socket               # Import socket module
import numpy as np
import time


debug = True

################################################################################
###                        HELPER FUNCTIONS                                  ###
################################################################################
def estConnection(host, port):
  """Establishes connection to the server
  Input:
    host:     Host Adress
    port:     Port for connection
  Return:
    int success: 1 if successfull"""
  sock = socket.socket()         # Create a socket object
  sock.connect((host, port))
  buff = sock.recv(1024)          # Handshake positive
  if (buff[0] == 'Y'):
    # Handshake positive
    print(buff[1:])
    return 1, sock
  else:
    return 0, None
    
    
    
def saveSend(sock, command):
  """Sends the command to the server and checks if the command
  was submitted correctly
  Inout:
    command:     string
  Return:
    int          successfull. Raises error if not."""
  sent = sock.send(command)
  for i in range(10):
    if (sent < len(command)) and debug:
      print('ERROR> During sending - Retry')
    else:      
      time.sleep(0.0005)
      return 1
  if (sent == 0):
    raise "ERROR> No communication with server possible"
    return 0
    
    
    
    
def mapRequest(sock, x, y):
  """Sends map request and parses return
  Input:
    x:    Row position
    y:    Col position
  Return:
    int   tile state at given position. The value corresponds to the 
          state as follows:
          0 - Unknown
          2 - Allready bombed in a previous round
          3 - Successfull hit in a previous round"""
  # =============================== SEND COMMAND ================================
  res = saveSend(sock, "M, {}, {}".format(x, y))

  # =============================== PARSE INPUT ================================+
  # time.sleep(0.01)
  buff = sock.recv(1024)        # Get Result
  splittedBuff = buff.split(',')
  if   splittedBuff[0] == 'I': 
    print('ERROR> Invalid Command')
    return -1
  elif splittedBuff[0] == 'R':
    try:    res = int(splittedBuff[1])
    except:
      raise "Error> Server returned non int result on Map request"
      return -1
    else:
      return res
  elif splittedBuff[0] == 'T' or splittedBuff[0] == 'N':
    print("Turn not initialated")
    return -1
  else:
    print(">>>" + buff)
    raise "ERROR> Unexpected server string"
      
      
      
      
def bomb(sock, x, y):
  """Sends bomb request and parses return
  Input:
    x:    Row position
    y:    Col position
  Return:
    int   Hit (1) or not hit (0)
    int   Ship destroyed (1) or not (0)"""
  # =============================== SEND COMMAND ================================
  res = saveSend(sock, "B, {}, {}".format(x, y))

  # =============================== PARSE INPUT ================================+
  buff = sock.recv(1024)        # Get Result
  splittedBuff = buff.split(',')
  if   splittedBuff[0] == 'I': 
    print('ERROR> Invalid Command')
    return -1, -1
  elif splittedBuff[0] == 'R':
    try:    
      res = int(splittedBuff[1])
      dest = int(splittedBuff[1])
    except:
      raise "Error> Server returned non int result on bomb request"
      return -1, -1
    else:
      return res, dest
  elif splittedBuff[0] == 'T' or splittedBuff[0] == 'N':
    print("Turn not initialated")
    return -1, -1
  else:
    raise "ERROR> Unexpected server string"
    

################################################################################
###                                MAIN                                      ###
################################################################################

# ======================== CONNECT TO SERVER ===================================
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
res, sock = estConnection(host, port)
time.sleep(0.0005)
if (res == 0):
  raise "ERROR> Connection could not be established"



# ============================ PLAY ROUND ======================================
# Handshake concept:
# Server:  Initiates turn with string "T"
# Client:  Answers with string "Y"
#
# After that the client can send up to 999 map requests
#       and can start one bomb
# After bombing the client must reinitiate the new turn as described above
#
# The game is terminated from the server by sending the string "EOG".
#
# Please ensure, that all steps of the handshake is correctly implemented in 
# the client. If that is not the case, you will run in an unsynced behaviour 
# and therefore a dead-loop

isEOG = False
rndCounter = 0
while not(isEOG):
  buff = sock.recv(1024)        # Receive "T" string to start term
  if (buff == 'T'):
    res = saveSend(sock, 'Y')   # Answer with string "Y"
    # -------------------- START OF ROUND --------------------------------------
    rndCounter += 1
    if (debug):
      print('==== TURN START ====')
    # ---------------- IMPLEMENT YOUR BOT HERE ---------------------------------
    
    if (rndCounter == 1):
      # First test: Invalid request
      if (mapRequest(sock, -1, 5) == -1):  res0="O"
      else: res0="X"
      if (mapRequest(sock,  0, 10) == -1): res1="O"
      else: res1="X"
      if (mapRequest(sock, -1, 10) == -1): res2="O"
      else: res2="X"
      if (mapRequest(sock,  4, 5) >= 0):   res3="O"
      else: res3="X"
      print("Test invalid requests: {}, {}, {}, {}".format(res0, res1, res2, res3))
      
      hit, dest = bomb(sock, -1, 0)
      if (hit == -1) and (dest == -1): res0 = "O"
      else: res0 = "X"
      print("Test invalid bomb: {}".format(res0))
    
    
  elif (buff == "EOG"):
    print("End of game")
    isEOG = True
  elif (buff[0] == "N"):
    print("Unsynced client behaviour")

sock.close                     # Close the socket when done
