import socket
import argparse
import urllib.request
from sys import exit, argv
from _thread import *

root_url = ""  # ESP's url, ex: http://192.168.102 (Esp prints it to serial console when connected to wifi)

def sendRequest(url):
    n = urllib.request.urlopen(url) # send request to ESP

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--host', required=True, help='Set the host address to connect')
parser.add_argument('-p', '--port', required=True, help='Set the port to connect to')
args = parser.parse_args()


# tryng to establish a connection
clientSocket = socket.socket()
host = args.host

# check is the port number specified is an integer
try:
    port = int(args.port)
except ValueError:
    print("error: port number should be an integer")
    exit(1)

# trying to connect to the server
print('Connecting to the server ...')
try:
    clientSocket.connect((host, port))
except socket.error as e:
    print(str(e))
    exit(1)

print("Connected to the server")

# Do your thing in this func
while True:
	resp = clientSocket.recv(1024).decode('utf-8')
	print(resp)

	try:
		# write your code here
		if(resp=="NORMAL"):
        		sendRequest(root_url+"/NORMAL")
        		print("Normal!")
		if(resp=="EXCITED"):
        		sendRequest(root_url+"/EXCITED")
        		print("Excited!")
		if(resp=="LOW"):
        		sendRequest(root_url+"/LOW")
        		print("Low!")
		if(resp=="STRESS"):
        		sendRequest(root_url+"/STRESS")
        		print("Stress!")
		if(resp=="OFF"):
        		sendRequest(root_url+"/OFF")
        		print("Off!")

	except:
		continue


    
# close the connection
clientSocket.close()
