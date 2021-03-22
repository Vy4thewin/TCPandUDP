import socket
import threading
import time
import os
import sys
#https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python is the code that derived the time function in this code

BUFFER=1024*4
client= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
data=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#create the control and data channels for UDP

Server=sys.argv[1]
Cport=int(sys.argv[2])
Dport=int(sys.argv[3])
#Server's Ip and ports entered in by the user

client.connect((Server,Cport))
Daddr=(Server,Dport)
while True:
        cmmd=input("Enter Command")
        client.send(cmmd.encode('utf-8'))
        #send command over to the server 

        a, b=cmmd.split()
        #used as a switch statment, if the command's action is LS/CHDIR just print the data from data channel.
        #GET/PUT, ready to send and recieve information to/from the server

        if a.lower()=="ls" or a.lower()=="cd":
            msg="ACK".encode('utf-8')
            data.sendto(msg,Daddr)
            recmsg, addr = data.recvfrom(BUFFER)
            print('Server response: ' + recmsg.decode('utf-8'))
        # if there is no incoming commands from Server, receive the message(s) from data channel and print
        else:
            print()
            #nothing just a placeholder

        if a.lower()== "put": 
            sendDup=0
            f=0
            #counters for sending duplicates and sending file length 
            filelen=str(os.stat(b).st_size)
            
            data.sendto(filelen.encode('utf-8'),(addr,Dport))
            with open(b,"rb") as file:
                while True:
                    data.settimeout(3)
                    time.sleep(1) 
                    #send out the text file length/Chunks in the loop 
                    #Let the server sleep for a second while a repsond comes back from the client
                    try:
                        data1,addr1=data.recvfrom(BUFFER)
                        f=1
                        #f=1 means the client ACK the file length and ready to send over the othe chunks
                        chunks=file.read(BUFFER)
                        if not chunks:
                            break 
                        data.sendto(chunks,addr1)
                        #if client sent a ACK back, read the buffer size from the file and sent it to client
                    except socket.timeout:
                        sendDup+=1
                        if sendDup != 3:
                            if f==0:
                                data.sendto(filelen.encode('utf-8'),('',Dport))
                            else:
                                 data.sendto(chunks,addr1)
                            #If F=0, the text length wasn't received and its retransmitted. 
                            #If f=1, then length is transmitted but a chunk was lost. Retransmitted the previous chunk
                        else:
                            print('Result transmission failed.Terminating')
                            exit
                        #after three attempts of sending data and no ACK return, print error message and cancel    
            file.close()
        elif a.lower() == "get":
            x=0
            smsg="ACK"
            #counter for the test length and the ACK messae
            msg, addr1= data.recvfrom(BUFFER).decode('utf-8')
            if msg:
                data.sendto(smsg.encode('utf-8'),addr1)
                #send ACK back to the server, so the server starts sending over chunks
                try:
                    filelen=int(msg)
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
                        chunks, addr1= data.recvfrom(BUFFER)
                        if not chunks:
                            break
                        data.sendto(smsg.encode('utf-8'),addr1)
                        file.write(chunks)
                        x+=BUFFER
                    file.close()
                print("file accpeted. Check the client's directory for the file :)")
            #if there is data from the server, compute the rest. 
        else:
            print()
        # nothing here

# disconnent when user sends out disconnect message to server, idk if there is a disconnect rememeber to add if there is
datachannel.close()
