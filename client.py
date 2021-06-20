import socket
import argparse
from sys import exit, argv

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


# DO YOUR THING INSIDE THIS
while True:
    # getting the response from the server
    # this will be a string
    resp = clientSocket.recv(1024).decode('utf-8')

    # DO YOUR THING BELOW THIS
    print(resp)


# close the connection
clientSocket.close()
