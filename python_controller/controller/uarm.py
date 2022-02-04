import serial
import time

class SerialUarm:
	def __init__(self, port, baud):
		super(SerialUarm, self).__init__()
		self.port = port
		self.baud = baud
		self.serialConnection = serial.Serial(port, baud)

	def get_port(self):
		return self.port
		
	def waitReady(self):
		while True:
			if self.serialConnection.inWaiting() > 0:
				if self.serialConnection.readline() == "ok":	# <-- change 'ok'
					return
			time.sleep(1/5)