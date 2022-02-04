import os
import serial
import threading
import time

class SerialArduino(threading.Thread):
	def __init__(self, port, baud):
		threading.Thread.__init__(self)
		self.mainframe = None
		self.port = port
		self.baud = baud
		self.serial_interface = serial.Serial(port, baud)
		self.command_blocking = False
		self.running = True
		self.ready = False


	# main method
	# parses serial input data and decides what to do with it
	# if it is a number, it is the return code of a previously issued command
	# if it is not, it is a control-change
	def run(self):
		self.wait_ready()

		# run until thread gets killed
		while self.running:

			# if data is recieved
			if self.serial_interface.inWaiting():

				# read line and remove \r\n
				line = self.serial_interface.readline().decode().replace('\r','').replace('\n','')

				# if line is a number in a certain range, it is the return of a command
				if ["-2", "-1", "0"].count(line): self.command_blocking = False

				# else it means the controller detected a user input
				else: self.parse_control_changes(line)


	# setter method for mainframe reference
	def set_mainframe(self, mainframe):
		self.mainframe = mainframe


	# used internally to wait until the arduino sends an "init"
	# once it has recieved it, it sets self.ready to True
	def wait_ready(self):
		# loop forever
		while True:

			# check if there is serial data waiting in the buffer
			if self.serial_interface.inWaiting():
				
				# if it matches 'init', set self.ready to True and return
				if self.serial_interface.readline().decode().replace('\r','').replace('\n','') == "init":
					self.ready = True
					return


	# halt the program until the arduino instance is ready
	def block_ready(self):
		while not self.ready: time.sleep(0.2)
		return


	# parses a line containing control changes
	# control changes always follow the following format:
	#  <D/A><ID>:<VALUE>
	# 
	# D stands for 'digital' and A for 'analog'
	# multiple ones can be chained using a '|'
	# examples:
	#  D1:1
	#  A1:42
	#  D1:1|A:42
	def parse_control_changes(self, line):
		for change in line.split('|'):
			print(change)
			if change.startswith('D'):
				button = change.split(':')[0]
				value = change.split(':')[1]
				if value == "1":
					self.mainframe.press_button(button)
				else:
					self.mainframe.release_button(button)

			elif change.startswith('A'):
				potentiometer = change.split(':')[0]
				potentiometer = change.split(':')[0]

			else:
				pass


	# sends a command and waites for a reply consisting of a return code
	# blocks until a return code is recieved in the thread's main function
	def wait_run_command(self, command):
		# write the command to the serial port
		# while ensuring it is terminated with exactly one newline
		self.serial_interface.write(command.replace('\n','').encode() + os.linesep.encode())
		
		# set self.blocking to True
		self.command_blocking = True

		# wait until the thread's main function sets self.blocking to False
		# This happens when it recieves a return code

		while self.command_blocking: pass
		return
		

	# shutdown the thread
	def shutdown(self):
		self.running = False
		self.serial_interface.write("die\n")
		self.serial_interface.close()
