import os
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
		self.serial_interface = serial.Serial(port, baud)
		
		self.temperature = "unknown"
		self.speed = 100
		self.device_name = ""
		self.hardware_version = ""
		self.firmware_version = ""

		self.running = False
		self.ready = False


	# main method
	# waits for return codes
	def run(self):
		self.wait_ready()
		self.device_name = self.get_device_name()
		self.hardware_version = self.get_hardware_version()
		self.firmware_version = self.get_firmware_version()


	# used internally to wait until the uarm sends a b'@5 V1\r\n'
	# once it has recieved it, it sets self.ready to True
	def wait_ready(self):
		# loop forever
		while True:

			# check if there is serial data waiting in the buffer
			if self.serial_interface.inWaiting():
				line = self.serial_interface.readline()
				if line.decode().replace('\r','').replace('\n','') == "@5 V1":
					self.ready = True
					return


	# halt the program until the uarm instance is ready
	def block_ready(self):
		while not self.ready: time.sleep(0.2)
		return


	def get_device_name(self) -> str:
		return self.run_querry_command("P2201")


	def get_hardware_version(self) -> str:
		return self.run_querry_command("P2202")


	def get_firmware_version(self) -> str:
		return self.run_querry_command("P2203")


	def start_laser(self):
		self.run_command("M2233 V1")


	def stop_laser(self):
		self.run_command("M2233 V0")


	def run_querry_command(self, command) -> str:
		self.serial_interface.write(command.replace('\n','').encode() + os.linesep.encode())
		while True:
			if self.serial_interface.inWaiting():
				line = self.serial_interface.readline()
				line = line.decode().replace('\r','').replace('\n','').replace("ok", "").replace(" ", "")
				return line


	def run_command(self, command):
		self.serial_interface.write(command.replace('\n','').encode() + os.linesep.encode())
		while True:
			if self.serial_interface.inWaiting:
				self.serial_interface.readline()
				return
