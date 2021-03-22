import socket
import threading
import time
import os
import sys
#https://stackoverflow.com/questions/59289299/why-is-socket-recv-sometimes-blocking-and-sometimes-not
# was the source used in developing the method of sending files in chunks by have a file length sent over and used as a counter as recv was stuck on waiting for the last byte chunk
BUFFER = 1024*4
Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create the socket vlient with its IP address and open for streaming

server=sys.argv[1]
CPort = int(sys.argv[2])
DPort = int(sys.argv[3])
# Channel and Data ports are created by command line arugments. Also get the IP address of the Server

Client.connect((server, CPort))
# connect to the available open server and complete the socket
datachannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
datachannel.connect((server, DPort))
# create the data channel socket with the connected client and connect to the
# server's, use to send non commands over
connect = True
while connect:
    cmmd = input("Enter Command")
    Client.send(cmmd.encode('utf-8'))
    # send out the command through the control channel

    a, b = cmmd.split()
    # this If else statement is acting as a switch between the commands of
    # (ls,cs) and (get,put) as there is a error where the client waits for a
    # repsonse from control pannel when it suppose to receive messages from the data channel
    # this if/else statement will switch setups between the two types, as it
    # will be ready to recevie the data channel's mesessges and print, or
    # send/receive packets of data to/from the server

    if a.lower() == "ls" or a.lower() == "cd":
        recmsg = datachannel.recv(BUFFER).decode('utf-8')
        print('Server response: ' + recmsg)
        # if there is no incoming commands from Server, receive the message(s) from data channel and print
    else:
        print()
        #fcmmd = Client.recv(BUFFER).decode('utf-8')

    if a.lower()== "put":
        # The client will open the text file to sent it over to the server to be uploaded
        filelen=str(os.stat(b).st_size)
        datachannel.send(filelen.encode('utf-8'))
        with open(b,'rb') as file:
            while True:
                chunks=file.read(BUFFER)
                datachannel.send(chunks)
                if not chunks: 
                    break
            file.close()
            # in the while loop, as the text file is read to the buffer.
            # the chunk is encoded and sent over to client to be processed. Repeat until there's nothing else to read
        # the while true statement was derived by the "for _in progress" in the receive the file in ThePythonCode
    elif a.lower() == "get":
        x=0
        filelen=datachannel.recv(BUFFER).decode('utf-8')
        #get the text file length for the counter
        try:
            filelen=int(filelen)
            y=0
            #if there is no bytes attached to text file size, just int the value and set y=0
        except ValueError:
          c,d=filelen.split("I",1)
          filelen=int(c.strip())
          y=1
          #if there was a expection, then separate by the starting letter and strip the whitespace. Set y=1, as it used a transition

        with open(b,"wb") as file:
            while x<filelen:
                if x==0 and y==1:
                    file.write(d.encode('utf-8'))
                    x+=BUFFER
                    #If there was a expection, take the bytes from the separation and add it to the file and increment the buffer
                chunks=datachannel.recv(BUFFER)
                if chunks.decode('utf-8','ignore')=="ACK": 
                    break
                file.write(chunks)
                x+=BUFFER
            # while loop is reading bytes sent over by server and writing into file.
            # Either stops because it reaches a empty string or x is greater than length of file. Tributed from stack over flow and office hours
            file.close()
        print("file accpeted. Check the client's directory for the file :)")
    else:
        print()
    # nothing here


datachannel.close()
Client.close()
# disconnent when user sends out disconnect message to server,  if there is a disconnect 