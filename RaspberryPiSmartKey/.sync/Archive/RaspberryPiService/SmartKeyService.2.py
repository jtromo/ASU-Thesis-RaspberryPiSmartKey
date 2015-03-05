__author__ = 'jtromo'
#Developed at : SEFCOM Labs by James Romo
from bluetooth import *
from Crypto.Cipher import AES
import threading
import time
import base64
import os
import uuid

# /////////////////////////////////////////////////////////////////////////////
#                               Configuration 
# /////////////////////////////////////////////////////////////////////////////

# ---------------------------------- Flags ------------------------------------

# Logging Level Controls
LOGGING_INFO                        = 1
LOGGING_DEBUG                       = 0
LOGGING_ERROR                       = 1

# Determines which protocol components need creation (if not, read from disk)
REQUIRES_SHARED_SECRET_GENERATION     = 1
REQUIRES_SMARTKEY_ID_GENERATION       = 1
REQUIRES_TRUSTED_DEVICES_GENERATION   = 1

# Causes the service to use a sample message from the device instead of real
DEBUG_USE_SAMPLE_DEVICE_MESSAGE     = 1
if DEBUG_USE_SAMPLE_DEVICE_MESSAGE:
    print '////////////////////////////////////////////////////////////////////'
    print '----------------------------- WARNING ------------------------------'
    print '                  ******* Testing Mode Enabled *******'
    print '        Using sample device message'
    print '        Must be disabled for demo'
    print '////////////////////////////////////////////////////////////////////'

# -------------------------------- Encryption ---------------------------------

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

# ---------------------- Protocol Components Generation -----------------------

# ********* shared_secretKey **********
# 1) Generate a new shared_secretKey (if required)
if REQUIRES_SHARED_SECRET_GENERATION:
    new_shared_secretKey = os.urandom(BLOCK_SIZE)
    if LOGGING_DEBUG:
        print 'Newly generated shared_secretKey:', new_shared_secretKey

# 2) Save new shared_secretKey to a file (if required)
if REQUIRES_SHARED_SECRET_GENERATION:
    with open('shared_secretKey', 'w') as file_: file_.write(new_shared_secretKey)
    if LOGGING_DEBUG:
        print 'Successfully saved new shared_secretKey'

# 3) Read shared_secretKey from file
shared_secretKeyFile = open('shared_secretKey')
read_shared_secretKey = shared_secretKeyFile.read()
if LOGGING_DEBUG:
    print 'shared_secretKey from file:', read_shared_secretKey

# 4) Create a cipher object using shared_secretKey
cipher = AES.new(read_shared_secretKey)

# *********** smartKey_id *************
# 5) Generate a new smartKey_id (if required)
if REQUIRES_SMARTKEY_ID_GENERATION:
    new_smartKey_id = uuid.uuid4()
    if LOGGING_DEBUG:
        print 'Newly generated smartKey_id:', new_smartKey_id

# 6) Save new smartKey_id to a file (if required)
if REQUIRES_SMARTKEY_ID_GENERATION:
    with open('smartKey_id', 'w') as file_: file_.write(new_smartKey_id)
    if LOGGING_DEBUG:
        print 'Successfully saved new smartKey_id'

# 7) Read shared_secretKey from file
smartKey_idFile = open('smartKey_id')
read_smartKey_id = smartKey_idFile.read()
if LOGGING_DEBUG:
    print 'smartKey_id from file:', read_smartKey_id

# ********** trusted_devices **********
# 8) Generate a new list of trusted_devices (if required)
if REQUIRES_TRUSTED_DEVICES_GENERATION:
    new_trusted_devices = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
    if LOGGING_DEBUG:
        print 'Newly generated trusted_devices:', new_trusted_devices

# 9) Save new list of trusted_devices to a file (if required)
if REQUIRES_TRUSTED_DEVICES_GENERATION:
    with open('trusted_devices', 'w') as file_: file_.write(new_trusted_devices)
    if LOGGING_DEBUG:
        print 'Successfully saved new trusted_devices'

# -------------------------- Protocol Components ------------------------------
smartKey_id = read_smartKey_id
shared_secretKey = read_shared_secretKey

# Sample from phone key
sample_device_id = uuid.uuid4()

# List of trusted device_ids
if DEBUG_USE_SAMPLE_DEVICE_MESSAGE:
    trusted_devices = [sample_device_id]
else:
    # TODO: Place generated uuid's here
    trusted_devices = ['trusted1', 'trusted2', 'trusted3', 'trusted4']

# /////////////////////////////////////////////////////////////////////////////
#                            Client Response Thread 
# /////////////////////////////////////////////////////////////////////////////

class ClientResponseThread (threading.Thread):
    def __init__ (self, socket):
		self.socket = socket
		threading.Thread.__init__(self)

	def run (self):
		try:
            # Generate timestamp for protocol
			timestamp = time.time()
            if LOGGING_DEBUG:
                print 'timestamp:', timestamp
			# Create decodedMsg: device_id, timestamp
			decodedMsg = smartKey_id + '-' + str(timestamp)
            if LOGGING_DEBUG:
                print 'decodedMsg:', decodedMsg

            # Encode message: secretKey(device_id, timestamp)
			encodedMsg = EncodeAES(cipher, decodedMsg)
			if LOGGING_DEBUG:
                print 'encodedMsg:', encodedMsg

            # Send response
			self.socket.send (encodedMsg)
		except:
            print "Fatal error has occurred during client response. Closing socket..."
            if LOGGING_ERROR:
                e = sys.exc_info()
                print 'Response Thread:', e
            self.socket.close()

# /////////////////////////////////////////////////////////////////////////////
#                              Smart Key Service 
# /////////////////////////////////////////////////////////////////////////////

# ---------------------- Bluetooth Socket Configuration -----------------------

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "a60f35f0-b93a-11de-8a39-08002009c666"

advertise_service(server_sock, "SmartKey", service_id=uuid,
                  service_classes=[uuid, SERIAL_PORT_CLASS], profiles=[SERIAL_PORT_PROFILE],
                 )
if LOGGING_INFO:
    print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
if LOGGING_INFO:
    print("Accepted connection from ", client_info)

# ---------------------------- Bluetooth Service ------------------------------

try:
    while True:
        # Retrieve data sent by mobile device
        data = client_sock.recv(1024)

        if len(data) > 0:
            if LOGGING_DEBUG:
                print("Encoded message received from mobile device: [%s]" % data)

            # ****** Verify the message came from trusted valid device ******
            try:
                # Decode encrypted message
                if DEBUG_USE_SAMPLE_DEVICE_MESSAGE:
                    # In place until Android encryption is finished
                    decoded_device_id = sample_device_id
                else:
                    decoded_device_id = DecodeAES(cipher, data)

                if LOGGING_DEBUG:
                    print 'Decoded device_id', decoded_device_id
                
                # Verify if device_id is in trusted_devices
                if decoded_device_id in trusted_devices:
                    if LOGGING_INFO:
                        print decoded_device_id, 'verified as a trusted device. Sending response...'
                    ClientResponseThread(client_sock).start()
                else:
                    if LOGGING_INFO:
                        print decoded_device_id, 'not found in list of trusted_devices'
        except:
            print 'Incorrect encrypted data format. Cannot be decoded.'
            if LOGGING_ERROR:
               e = sys.exc_info()
                print 'Decode:', e
        else:
                if LOGGING_DEBUG:
                    print 'No data has been received received'
except :
    print 'Fatal error has occurred during bluetooth service. Disconnecting...'
    if LOGGING_ERROR:
        e = sys.exc_info()
        print 'Bluetooth Service:', e

# --------------------------------- Exiting -----------------------------------

print("Smart Key Bluetooth Service has stopped.")

# Close all sockets
client_sock.close()
server_sock.close()

print("Please Restart service.")
