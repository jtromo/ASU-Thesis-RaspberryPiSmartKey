__author__ = 'jtromo'
#Developed at : SEFCOM Labs by James Romo
#With assistance from :  JJ SEO and Clinton Dsouza
from bluetooth import *
import threading
import time
from Crypto.Cipher import AES
import base64
import os

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
secret = os.urandom(BLOCK_SIZE)
print 'Secret Key:', secret
with open("SecretKey.txt", "w") as text_file: text_file.write(secret)

# create a cipher object using the random secret
cipher = AES.new(secret)

# encode a string
encoded = EncodeAES(cipher, 'password')
print 'Encrypted string:', encoded

# decode the encoded string
decoded = DecodeAES(cipher, encoded)
print 'Decrypted string:', decoded

class MyThread (threading.Thread):
	def __init__ (self, socket):
		self.socket = socket
		threading.Thread.__init__(self)

	def run (self):
		try:
                        # Protocol Components
                        device_id = "device_id"
                        shared_secretKey = "secretKey"
			userInput = raw_input('Enter your input:')
			print 'Input:', userInput
			timestamp = time.time()
			print 'Timestamp:', timestamp
			# send secretKey(device_id, timestamp)
			print 'Device_id:', device_id
			decodedMsg = device_id + timestamp
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
	MyThread(client_sock).start()
        data = client_sock.recv(1024)
        if len(data) == 0:
            break
        print("received [%s]" % data)
        with open("STS.json","a") as myfile:
            myfile.write('\n'+data)
except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()

print("all done")
