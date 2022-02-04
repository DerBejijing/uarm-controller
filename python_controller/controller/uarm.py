import serial
import threading
import time

###############
# not used yet
###############

class SerialUarm(threading.Thread):
	def __init__(self, port, baud):
		threading.Thread.__init__(self)
		self.port = port
		self.baud = baud
		self.serialConnection = serial.Serial(port, baud)
		self.running = True
		self.ready = False


	# main method
	# waits for return codes
	def run(self):
		self.wait_ready()

		# run until thread gets killed
		while self.running:

			# if data is recieved
			if self.serial_interface.inWaiting():

				# read line and remove \r\n
				line = self.serial_interface.readline().decode().replace('\r','').replace('\n','')
