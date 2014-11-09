#!/usr/bin/python

import socket
import os

sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = input("Provide the port number to which event will be sent: ")
sd.bind((os.getenv('HOST'),port))

sd.listen(10)
print "Listening on port " + str(port)

file = raw_input("Provide the BFT File name : ")
record_count = input("Provide number of records required in file : ")

fd = open(file, "wb")

while record_count != 0:

	a,c = sd.accept()
	print "Recieved some data on socket..."

	data = a.recv(2048)
	print "Received data size is : " + str(len(data))

	fd.write(data)
	a.close()

	record_count = record_count - 1

fd.close()
sd.close()
