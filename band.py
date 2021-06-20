import argparse
import subprocess
import time
import signal
import csv
import math
import socket
from datetime import datetime
from _thread import *

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import psutil
import collections

from bluepy.btle import BTLEDisconnectError

from constants import MUSICSTATE
from miband import miband

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mac', required=False, help='Set mac address of the device')
parser.add_argument('-k', '--authkey', required=False, help='Set Auth Key for the device')
parser.add_argument('-f', '--file', required=True, help='Set the output path to save heart rate data')
parser.add_argument('-a', '--host', required=False, default='127.0.0.1', help='Set the host address to connect')
parser.add_argument('-p', '--port', required=True, help='Set the port to connect to')
args = parser.parse_args()

# Try to obtain MAC from the file
try:
    with open("mac.txt", "r") as f:
        mac_from_file = f.read().strip()
except FileNotFoundError:
    mac_from_file = None

# Use appropriate MAC
if args.mac:
    MAC_ADDR = args.mac
elif mac_from_file:
    MAC_ADDR = mac_from_file
else:
    print("Error:")
    print("  Please specify MAC address of the MiBand")
    print("  Pass the --mac option with MAC address or put your MAC to 'mac.txt' file")
    print("  Example of the MAC: a1:c2:3d:4e:f5:6a")
    exit(1)

# Validate MAC address
if 1 < len(MAC_ADDR) != 17:
    print("Error:")
    print("  Your MAC length is not 17, please check the format")
    print("  Example of the MAC: a1:c2:3d:4e:f5:6a")
    exit(1)

# Try to obtain Auth Key from file
try:
    with open("auth_key.txt", "r") as f:
        auth_key_from_file = f.read().strip()
except FileNotFoundError:
    auth_key_from_file = None

# Use appropriate Auth Key
if args.authkey:
    AUTH_KEY = args.authkey
elif auth_key_from_file:
    AUTH_KEY = auth_key_from_file
else:
    print("Warning:")
    print("  This program requires the auth key. Please put your Auth Key to 'auth_key.txt' or pass the --authkey option with your Auth Key")
    print()
    exit(1)
    
# Validate Auth Key
if AUTH_KEY:
    if 1 < len(AUTH_KEY) != 32:
        print("Error:")
        print("  Your AUTH KEY length is not 32, please check the format")
        print("  Example of the Auth Key: 8fa9b42078627a654d22beff985655db")
        exit(1)
else:
    exit(1)

# Convert Auth Key from hex to byte format
AUTH_KEY = bytes.fromhex(AUTH_KEY)

# stores the heart rate
heartLog = []
bpm = []
neutralHR = 84

# interval between each heart rate measure
hrtInterval = 0
# start time
strtTime = 0

# sliding window for analysing data
window = 100

# stores all the clients
clientList = []

# saves the log
def saveLog():
    global heartLog
    
    # writing the heartLog
    with open(args.file, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
      
        # writing the fields
        csvwriter.writerow(['crnt_time', 'interval', 'time', 'bpm', 'data_mean', 'norm_data', 'norm_median', 'data_entropy', 'norm_diff1'])
      
        # writing the data rows
        csvwriter.writerows(heartLog[1:])


# functions related to heart rate analysis
def EMA(bpm, index, window, factor=0.04):
    if window > index:
        lst = bpm[:index+1]
    else:
        lst = bpm[index - window:index+1]

    dat = []
    dat.append(lst[0])

    for i in range(1, len(lst)):
        dat.append(factor*lst[i] + (1-factor)*dat[i-1])

    return dat[-1]

def median_hr(bpm, index, window):
    if window > index:
        lst = bpm[:index+1]
    else:
        lst = bpm[index - window:index+1]

    n = len(lst)
    lst.sort()

    if n % 2 == 0:
        median1 = lst[n//2]
        median2 = lst[n//2 - 1]
        return (median1 + median2)/2
    else:
        return lst[n//2]

def entropy(bpm, index, window):
    if window > index:
        lst = bpm[:index+1]
    else:
        lst = bpm[index - window:index+1]

    ent = 0
    for i in range(len(lst)):
        p = lst.count(lst[i]) / len(lst)
        ent += p * math.log2(p)

    return -ent

def diff1(bpm, index, window):
    if index == 0:
        return bpm[0]
    elif window > index:
        lst = bpm[:index+1]
    else:
        lst = bpm[index - window:index+1]
    
    diff = 0
    for i in range(1, len(lst)):
        diff += abs(lst[i] - lst[i-1])

    return diff / (len(lst)-1)




# Needs Auth
def get_heart_rate():
    print ('Latest heart rate is : %i' % band.get_heart_rate_one_time())
    input('Press a key to continue')

def classify(log):
    hr = log[3]
    ent = log[7]
    if hr > 95 and ent > 32:
        return 'STRESS'
    elif hr > 95 and ent < 32:
        return 'EXCITED'
    elif hr < 75 and ent > 32:
        return 'LOW'
    else:
        return 'NORMAL'

def process_data(data, interval):
    global heartLog, strtTime, window, bpm, neutralHR, clientList

    crntTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    index = len(heartLog) 

    data_mean = EMA(bpm, index, window, 0.04)
    norm_data = bpm[index] - neutralHR
    norm_median = median_hr(bpm, index, window) - neutralHR
    data_entropy = entropy(bpm, index, window)
    norm_diff1 = diff1(bpm, index, window)


    log = [crntTime, interval, time.time() - strtTime, data, data_mean, norm_data, norm_median, data_entropy, norm_diff1]
    heartLog.append(log)
    print(log)


    # send data to the clients
    if len(clientList) != 0:
        for client in clientList:
            # this is to ensure that even if one of the clients connections is 
            # broken, the program continues to function.
            try:
                client.sendall(str.encode(classify(log)))
            except BrokenPipeError:
                continue

   
    # save the log in intervals so that all data in case of error
    if len(heartLog) % 50 == 0:
        print('saved')
        saveLog()

def heart_logger(data):
    global hrtInterval, bpm


    hrtInterval = time.time() - hrtInterval
    bpm.append(data)

    # start new thread to process data
    start_new_thread(process_data, (data, hrtInterval,))
    hrtInterval = time.time()

    

# Needs Auth
def get_realtime():
    band.start_heart_rate_realtime(heart_measure_callback=heart_logger)
    input('Press Enter to continue')



# adds client to the list
def addClient(bandSocket):
    global clientList

    for i in range(50):
        # connects to the client and adds them to the clientList
        client, address = bandSocket.accept()

        clientList.append(client)

        print(f'Connected to client {i} at ' + address[0] + ' : ' + str(address[1]))




# visualization 
bpmPlot = collections.deque(np.zeros(window))
entPlot = collections.deque(np.zeros(window))


# function to update the data
def plot_function(bpm, ent):
    # get data
    bpmPlot.popleft()
    bpmPlot.append(bpm)
    entPlot.popleft()
    entPlot.append(ent)    

    # clear axis
    ax.cla()
    ax1.cla()    

    # plot heart rate
    ax.plot(bpmPlot)
    ax.scatter(len(bpmPlot)-1, bpmPlot[-1])
    ax.text(len(bpmPlot)-1, bpmPlot[-1]+2, "{} bpm".format(bpmPlot[-1]))
    ax.set_ylim(60,130)    

    # plot entropy
    ax1.plot(entPlot)
    ax1.scatter(len(entPlot)-1, entPlot[-1])
    ax1.text(len(entPlot)-1, entPlot[-1]+2, "{} bits".format(entPlot[-1]))
    ax1.set_ylim(0,100)

# define and adjust figure
fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
ax = plt.subplot(121)
ax1 = plt.subplot(122)
ax.set_facecolor('#DEDEDE')
ax1.set_facecolor('#DEDEDE')






# exception handling
def signal_handler(sig, frame):
    print('saving the log')
    saveLog()
    
    print('\nExiting')
    exit(0)

if __name__ == "__main__":
    # ensure that the port number is an integer
    try:
        port = int(args.port)
    except ValueError:
        print("error: port number should be an integer")
        exit(1)

    # initialize the socket
    bandSocket = socket.socket()

    # try establishing the connection
    try:
        bandSocket.bind((args.host, int(args.port)))
    except socket.error as e:
        print(str(e))
        exit(1)


    signal.signal(signal.SIGINT, signal_handler)

    success = False
    while not success:
        try:
            if (AUTH_KEY):
                band = miband(MAC_ADDR, AUTH_KEY, debug=True)
                success = band.initialize()
            else:
                band = miband(MAC_ADDR, debug=True)
                success = True
            break
        except BTLEDisconnectError:
            print('Connection to the MIBand failed. Trying out again in 3 seconds')
            time.sleep(3)
            continue
        except KeyboardInterrupt:
            print("\nExit.")
            exit()

   
    # listen to the connection requests
    bandSocket.listen()

    start_new_thread(addClient, (bandSocket,))


    # initializing time
    strtTime = hrtInterval = time.time()

    start_new_thread(get_realtime, ())

    while True:
        if heartLog:
            plot_function(heartLog[-1][3], heartLog[-1][7])
            plt.pause(1)

    plt.show()
