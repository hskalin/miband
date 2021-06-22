# Mi Band based Biometrics Automation

This ia a small set of scripts that uses a library to connect with the Mi band 4/5 and get realtime heart rate and step count data. Then the data can be analysed and many useful things can be done with it, like predicting the mood and controlling lighting based on mood etc.

## getting the real time mood data
The band.py scrip gets the data from the watch and it also transmits the estimated mood to a specified port. In order to access this data one can use the client.py script.

## connecting and sending requests to nodeMCU ESP8266
The ledControl.ino sets the pin to HIGH or LOW depending on the request sent
The Send_req.py script gets the data from the port and sends a request to the ESP through wifi

## credits
[satcar77/miband4](https://github.com/satcar77/miband4) - we have used this python library that allows to interact with the Mi band
[kebabLord/esp2python](https://github.com/KebabLord/esp2python) - We have used this library to connect the ESP8266 module to a wifi and send requests to the module
