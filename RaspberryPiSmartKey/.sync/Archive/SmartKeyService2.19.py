__author__ = 'jtromo'
#Developed at : SEFCOM Labs by James Romo
#With assistance from :  JJ SEO and Clinton Dsouza
from bluetooth import *
import threading
import time
from Crypto.Cipher import AES
import base64
import os
from math import *

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

# generate a random secret key
#secret = os.urandom(BLOCK_SIZE)
#print 'Secret Key:', secret

# save secret key to file
#with open('SecretKey', 'w') as file_: file_.write(secret)

# read secret key from file
secretFile = open('SecretKey')
secret = secretFile.read()
print 'Read Secret Key:', secret

# create a cipher object using the random secret
cipher = AES.new(secret)

# encode a string
encoded = EncodeAES(cipher, 'password')
print 'Encrypted string:', encoded

# decode the encoded string
decoded = DecodeAES(cipher, encoded)
print 'Decrypted string:', decoded

# Protocol Components
smartKey_id = 'smartKey_id'
shared_secretKey = secret

# Sample from phone key
device_id = 'keyFromAndroid'

class MyThread (threading.Thread):
	def __init__ (self, socket):
		self.socket = socket
		threading.Thread.__init__(self)

	def run (self):
		try:
                        print "shared_secretKey:", shared_secretKey
			#userInput = raw_input('Enter your input:')
			#print 'Input:', userInput
			timestamp = time.time()
			print 'Timestamp:', timestamp
			# send secretKey(device_id, timestamp)
			print 'smartKey_id:', smartKey_id
			decodedMsg = smartKey_id + '-' + str(timestamp)
			print 'Decoded Message:', decodedMsg
			encodedMsg = EncodeAES(cipher, decodedMsg)
			print 'Encoded Message:', encodedMsg
			self.socket.send (encodedMsg)
		except:
                        e = sys.exc_info()
                        print 'Crash:', e
			self.socket.close()
			print "socket close"
		
server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "a60f35f0-b93a-11de-8a39-08002009c666"

advertise_service(server_sock, "SmartKey", service_id=uuid,
                  service_classes=[uuid, SERIAL_PORT_CLASS], profiles=[SERIAL_PORT_PROFILE],
                 )

print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

try:
    while True:
        data = client_sock.recv(1024)
        # Data must be a multiple of 16 in length
        length = len(data)
        if length % 16 == 0
        #if len(data) % 16 == 0
        #if len(data) > 0:
                print("received [%s]" % data)


                # Test to see if came from valid device
                # Decode data
                print 'Encoded Message', data
                decodedDeviceId = DecodeAES(cipher, data)
                print 'Decoded device_id', decodedDeviceId
                # Check if a known device id
                # if (decodedDeviceID matches any in list)
                
                with open("STS.json","a") as myfile:
                    myfile.write('\n'+data)
                MyThread(client_sock).start()
        else
                print 'Data must be a multiple of 16 in length'
except IOError:
    e = sys.exc_info()
    print 'Crash:', e
    pass

print("disconnected")

client_sock.close()
server_sock.close()

print("all done")
