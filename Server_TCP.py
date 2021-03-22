import socket
import threading
import time
import os
import sys
# https://stackoverflow.com/questions/59289299/why-is-socket-recv-sometimes-blocking-and-sometimes-not
# was the source used in developing the method of sending files in chunks AND closing the file on the read side
# Also,https://www.youtube.com/watch?v=3QiPPX-KeSc&list=PLq2jrhLHUlWLqEhCzu1cWb-7rpSY5H4N7&index=72&t=1744s&ab_channel=TechWithTim
#was use in the threading method of mutlithreading TCP Clients 
BUFFER = 1024*4
CPort = int(sys.argv[1])
Server = "169.226.22.18"
#can't used socket.gethostbyname(gethostname()) nor localhost and "0.0.0.0" as it will send error that window actively refuses
#If test on two commands on the same laptop, Server=gethostbyname(gethostname())
#get ip addresss of the server and assigning server's control/data channels

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((Server,CPort))
#creates the control socket and the welcome socket is now bound to the server's address
DPort = int(sys.argv[2])
datachannel = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
datachannel.bind((Server,DPort))
#creates the data channel socket
def ConnectClient(c,addr,data,addr1):
    print("Client {0} is connected!".format(addr))
    #Tells user that the client has connected to the server, prints out the
    #client's ip
    #the while keeps the socket open
    ClienCon = True
    while ClienCon:
        currDirectory = os.getcwd()
        cmmd = c.recv(BUFFER).decode("utf-8")
        a,b = cmmd.split()
        #split the command line into the command prompt and path
        if a.lower() == 'ls':
            list= os.listdir(currDirectory)
            lists="{0}".format(list)
            data.send(lists.encode('utf-8'))
            #sends a list of programs in the current directory throught the
            #data channel to the client
        elif a.lower() == 'cd':
            os.chdir(b)
            msg="{0} is now changed to {1}".format(currDirectory,b)
            data.send(msg.encode('utf-8'))
            #changes the current directory to the path given by user and send a
            #conformation to the client about the change
        elif a.lower() == 'get':
            c.send(cmmd.encode('utf-8'))
            #sends command to client, as a alert for the client side to prepare
            #to do action
            filelen=str(os.stat(b).st_size)
            data.send(filelen.encode('utf-8'))
            #send text file size to the client before sending the file over

            with open(b,"rb") as file:
                while True:
                    chunks= file.read(BUFFER)
                    if not chunks: 
                        data.send("ACK".encode('utf-8'))
                        break
                    data.send(chunks)
                file.close()
               #in the while loop, as the text file is read to the buffer.
               #the chunk is encoded and sent over to client to be processed.
              # Repeat until there's nothing else to read
            
            #the file is close once sent over
            #the while true statement was derived by the "for _in progress"
            #loop in the receive the file in ThePythonCode
        elif a.lower() == 'put':
            x=0
            c.send(cmmd.encode('utf-8'))
            filelen=data.recv(BUFFER).decode('utf-8')
            #Get the text file's length for the incoming text file
           
            try:
                filelen=int(filelen)
                y=0
                #If the size of the incoming is not attached to a byte stream, just convert the str into a int again 
            except ValueError:
               c,d=filelen.split("I",1)
               filelen=int(c.strip())
               y=1
               #If there is bytes other than the text length, seperate by the first I and strip any white space. Set y=1, as it used a transition
        
            #create the text file and insert the text file in the current directory in a while loop, either x reaches file length or ACK is received 
            with open(b,"wb") as file:
                while x <filelen:
                    if x==0 and y==1:
                        file.write(d.encode('utf-8'))
                        x+=BUFFER
                        #If there was a expection, take the bytes from the separation and add it to the file and increment the buffer
                    chunks=data.recv(BUFFER)
                    if chunks.decode('utf-8','ignore') =="ACK":
                        break
                    file.write(chunks)
                    x+=BUFFER
            # while chunks come over, we check if the chunks received aren't empty and enter in the file. If the counter is over the file length close the file
            file.close()
            print("Uploaded to Server. Check Server's Directory for the file")
           #Found the reason for not available chunks issuse through https://stackoverflow.com/questions/59289299/why-is-socket-recv-sometimes-blocking-and-sometimes-not
        elif a.lower() == 'disconnect':
            data.send("Client sent a disconnect request, goodbye!".encode('utf-8'))
            data.close()
            ClienCon = False
            #close the connect of the server. Please ask if we have to implement this or i'm wasting time :()
        else:
            data.send("Command not found, try again".encode('utf-8'))
    c.close()

server.listen(3)
datachannel.listen(1)
#data channel will only have a queue of one, as it connecting to its client's
#request
print("The server is open for new connections :)")
while True:
    data, addr1 = datachannel.accept()
    c, addr = server.accept()
    t1 = threading.Thread(target=ConnectClient, args=(c,addr,data,addr1))
    t1.start()
    #thread over the contents of the control/data sockets over to connectclient method to handle the client's request






  

            