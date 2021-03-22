import socket
import threading
import time
import os
import sys
# https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python is the code that derived the time function in this code

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
datachannel=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
datadd=('',DPort)
datachannel.bind(('',DPort))
#create the data channel 
def ConnectClient(c,addr,datachannel):
    print("Client {0} is connected!".format(addr))
    #Tells user that the client has connected to the server, prints out the client's ip
    ClienCon = True
    while ClienCon:
       currDirectory = os.getcwd()
        #client data and control channels are connected and ready for packets

       cmmd = c.recv(BUFFER).decode("utf-8")
       a, b = cmmd.split()
       # split the command line into the command prompt and path
       if a.lower() == "cd":
           message, addr1= datachannel.recvfrom(BUFFER)
           if not message:
               print("Begin ACK not received")
               break
           #the "third" handshake, Client is ready for Server to send over data and it gives the sending address
           os.chdir(b)
           msg="{0} is now changed to {1}".format(currDirectory,b)
           datachannel.sendto(msg.encode('utf-8'),addr1)
           #change directory and send confirmation through data channel

       elif a.lower()=="ls":
           message, addr1= datachannel.recvfrom(BUFFER)
           if not message:
               print("ACK not received")
               break
            #The final handshake before data send over

           list=os.listdir(b)
           lists="{0}".format(list)
           datachannel.sendto(lists.encode('utf-8'),addr1)
           #sends a list of programs in the current directory throught the data channel to the client

       elif a.lower()=="get":
           sendDup = 0
           f = 0
           #counters for sending duplicates and sending file length

           filelen = str(os.stat(b).st_size)
           datachannel.sendto(filelen.encode('utf-8'), )
           with open(b, "rb") as file:
               while True:  
                   datachannel.settimeout(3)
                   time.sleep(1)
                   #send out the text file length/Chunks in the loop
                   #Let the server sleep for a second while a repsond comes back from the client
                   try:
                        data1, addr1 = datachannel.recvfrom(BUFFER)
                        f = 1
                        #f=1 means the client ACK the file length and ready to send over the othe chunks
                        chunks = file.read(BUFFER)
                        if not chunks:
                            break
                        datachannel.sendto(chunks, addr1)
                        #if client sent a ACK back, read the buffer size from the file and sent it to client
                   except socket.timeout:
                        sendDup += 1
                        if sendDup != 3:
                            if f == 0:
                                datachannel.sendto(filelen.encode('utf-8'),addr1)
                            else:
                                datachannel.sendto(chunks, addr1)
                            #If F=0, the text length wasn't received and its retransmitted.
                            #If f=1, then length is transmitted but a chunk was lost. Retransmitted the previous chunk
                        else:
                            print('Result transmission failed.Terminating')
                            exit
                        #after three attempts of sending data and no ACK return, print error message and cancel
       elif a.lower()=="put":
            x=0
            msg="ACK".encode('utf-8')
            filelen, addr =datachannel.recv(BUFFER).decode('utf-8')
            #Get the text file's length from the first message from
        
            try:
                filelen=int(filelen)
                y=0
                datachannel.sendto(msg,addr)
                #If the size of the incoming is not attached to a byte stream, just convert the str into a int again 
            except ValueError:
               c,d=filelen.split("I",1)
               filelen=int(c.strip())
               y=1
               datachannel.sendto(msg,addr)
               #If there is bytes other than the text length, seperate by the first I and strip any white space. Set y=1, as it used a transition
            time.sleep(1)
            #create the text file and insert the text file in the current directory in a while loop, either x reaches file length or ACK is received 
            with open(b,"wb") as file:
                while x <filelen:
                    chunks, addr1 =datachannel.recv(BUFFER)
                    if not chunks:
                        print("Did not receive valid data from client.Terminating")
                        break
                    if x==0 and y==1:
                        file.write(chunks.encode('utf-8'))
                        x+=BUFFER
                        datachannel.sendto(msg,addr1)
                        #If there was a expection, take the bytes from the separation and add it to the file and increment the buffer
                    file.write(chunks)
                    x+=BUFFER
                    datachannel.sendto(msg,addr)
            # while chunks come over, we check if the chunks received aren't empty and enter in the file. If the counter is over the file length close the file
            file.close()
       else:
         print()
    c.close()
server.listen(3)
#data channel will only have a queue of one, as it connecting to its client's
#request
print("The server is open for new connections :)")
while True:
    c, addr = server.accept()
    t1 = threading.Thread(target=ConnectClient, args=(c,addr,datachannel))
    t1.start()
    #thread over the contents of the control/data sockets over to connectclient method to handle the client's request




