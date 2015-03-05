__author__ = 'cvdsouza'
#Developed at : SEFCOM Labs by JJ SEO and Clinton Dsouza
from bluetooth import *
import threading

class MyThread (threading.Thread):
	def __init__ (self, socket):
		self.socket = socket
		threading.Thread.__init__(self)

	def run (self):
		try:
			str = raw_input('Enter your input:')
			self.socket.send (str)
		except:
			self.socket.close()
			print "socket close"
		

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "a60f35f0-b93a-11de-8a39-08002009c666"
#uuid = "04c6093b-0000-1000-8000-00805f9b34fb"
#uuid = "84f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service(server_sock, "SampleServer", service_id=uuid,
                  service_classes=[uuid, SERIAL_PORT_CLASS], profiles=[SERIAL_PORT_PROFILE],
#                   protocols = [ OBEX_UUID ]
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
