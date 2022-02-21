import os
import psutil
import random

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.padding import Padding

import socket
import subprocess
import sys

import threading
import time


class Mainframe(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.arduino = None;
		self.uarm = None
		self.selected_item = 0
		self.display_changed = False
		self.buttons_changed = False
		self.items = 7
		self.buttons = 7

		self.display_timer = 0

		# initialize array of button states
		self.button_states = [0 for _ in range(self.buttons)]
		self.button_states_old = [0 for _ in range(self.buttons)]


	def init_devices(self, arduino_port, uarm_port):
		from . import arduino
		from . import uarm
		self.arduino = arduino.SerialArduino(arduino_port, 9600)
		self.arduino.set_mainframe(self)
		self.arduino.start()
		self.arduino.block_ready()
		self.uarm = uarm.SerialUarm(uarm_port, 115200)
		self.uarm.start()
		self.uarm.block_ready()


	# perform a button press
	# the value is then stored in self.button_states
	def press_button(self, button):
		button = int(button.replace('D', ''))
		if button < 0: button = 0
		elif button > self.buttons-1: button = self.buttons-1

		self.button_states[button] = 1
		self.buttons_changed = True


	# perform a button release
	# the value is then stored in self.button_states
	def release_button(self, button):
		button = int(button.replace('D', ''))
		if button < 0: button = 0
		elif button > self.buttons-1: button = self.buttons-1

		self.button_states[button] = 0
		self.buttons_changed = True


	# generate a list with all programs the user can choose from
	# it takes an integer as argument that specifies which element to highlight
	def _generate_list(self, active_element):
		# ensure that active_element is in a valid range
		if active_element < 0: active_element = 0
		elif active_element > self.items-1: active_element = self.items-1

		# list where all Panels are stored in
		item_list = []

		# lambda function to decide whether or not a certain panel should be highlighted
		get_style = lambda index : "red" if index==active_element else "white"

		# append each panel to the list
		item_list.append(Panel("Shutdown System", box=box.SQUARE, style=get_style(0)))
		item_list.append(Panel("Manual Control", box=box.SQUARE, style=get_style(1)))
		item_list.append(Panel("Laser", box=box.SQUARE, style=get_style(2)))
		item_list.append(Panel("Gripper", box=box.SQUARE, style=get_style(3)))
		item_list.append(Panel("...", box=box.SQUARE, style=get_style(4)))
		item_list.append(Panel("...", box=box.SQUARE, style=get_style(5)))
		item_list.append(Panel("...", box=box.SQUARE, style=get_style(6)))
		item_list.append(Panel("", box=box.SIMPLE))

		# return list
		return item_list


	# generates the layout representing all data
	def _generate_layout(self) -> Layout:
		# layout object
		layout = Layout()

		# split into header, main and footer
		layout.split(
			Layout(Panel(Padding(Align("[purple]UArm control mainframe[/purple]", "center"), (1, 1)), box=box.SQUARE), name="header", size=5),
			Layout(Panel("", box=box.SQUARE), name="main", ratio=1),
			Layout(Panel(Padding(Align("[purple]Software developed by Der_Bejijing (https://github.com/DerBejijing)[/purple]", "center"), (1, 1)), box=box.SQUARE), name="footer", size=5)
		)

		# split main into a panel that will act as a list to
		#  let the user choose from a variety of different programs
		#  using the buttons
		# and a panel listing information about the system
		layout["main"].split_row(
			Layout(Panel("", box=box.SQUARE), name="left"),
			Layout(Panel("", box=box.SQUARE), name="right", ratio=3),
		)


		# split into 2 areas
		# the names are choosen arbitrarily and do not represent their real function as I found out later
		# which is stupid, of course
		layout["right"].split(
			Layout(Panel("", title="UArm Info", box=box.SQUARE), name="uarm_info"),
			Layout(Panel("", box=box.SQUARE), name="system_info", ratio=3)
		)


		# set uarm_running
		if self.uarm.running: uarm_running = "[green]yes[/green]"
		else: uarm_running = "[red]no[/red]"

		# set uarm_temperature from self.uarm
		if self.uarm.temperature == "unknown": uarm_temperature = "[yellow]unknown[/yellow]"
		else: uarm_temperature = "[green]{}°C[/green]".format(self.uarm.uarm_temperature)
		uarm_temperature = self.uarm.temperature

		# split into 2 Panels showing data about uArm and LASER
		layout["uarm_info"].split_row(
			Layout(Panel(Padding(Align("uArm speed: [green]{}[/green]\nuArm running: {}\nuArm temperature: {}".format(self.uarm.speed, uarm_running, uarm_temperature)), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("uArm device name: [green]{}[/green]\nuArm hardware version: [green]{}[/green]\nuArm firmware version: [green]{}[/green]".format(self.uarm.device_name, self.uarm.hardware_version, self.uarm.firmware_version)), (1, 1)), box=box.SIMPLE))
		)


		# split the other (bigger) panel into three smaller panels
		layout["system_info"].split(
			Layout(name="system_info_1"),
			Layout(name="system_info_2"),
			Layout(name="system_info_3")
		)


		# split into 2 Panels showing CPU and RAM data
		layout["system_info_1"].split_row(
			Layout(Panel(Padding(Align("CPU frequency: {}\nCPU usage: {}\nCPU temperature: {}".format(SystemInfo.get_cpu_freq(), SystemInfo.get_cpu_usage(), SystemInfo.get_cpu_temp())), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("Memory available: {}\nMemory usage: {}\nMemory used: {}".format(SystemInfo.get_memory_available(), SystemInfo.get_memory_usage(), SystemInfo.get_memory_used())), (1, 1)), box=box.SIMPLE))
		)


		# collect information about network
		network_state = SystemInfo.get_network_state()
		network_name = "[yellow]----------[/yellow]"
		network_speed = "[yellow]---------[/yellow]"
		network_connection_type = SystemInfo.get_network_type()
		network_ip = SystemInfo.get_ip()
		network_interface = SystemInfo.get_active_network_interface_name(network_ip)
		network_mac = SystemInfo.get_mac(network_interface)


		# split into 2 Panels showing network information
		layout["system_info_2"].split_row(
			Layout(Panel(Padding(Align("Network state: {}\nNetwork name: {}\nNetwork speed: {}".format(network_state, network_name, network_speed)), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("Connection Type: {}\nIP: [green]{}[/green]\nMAC: [green]{}[/green]".format(network_connection_type, network_ip, network_mac)), (1, 1)), box=box.SIMPLE))
		)


		# split into 2 Panels showing SSH and cooling data
		layout["system_info_3"].split_row(
			Layout(Panel(Padding(Align("LASER enabled: {}\nLASER active: {}\nLASER power: {}".format("", "", "")), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("Fan speed 1: {}\nFan speed 2: {}\nFan speed 3: {}".format("", "", "")), (1, 1)), box=box.SIMPLE))
		)



		# generate a list containing all programs
		item_list = self._generate_list(self.selected_item)

		# insert all programs into the previously generated area
		# the names are arbitrary, as they will not be used to determine the active element
		layout["left"].split(
			Layout(item_list[0], name="a", size=4),
			Layout(item_list[1], name="a", size=4),
			Layout(item_list[2], name="a", size=4),
			Layout(item_list[3], name="a", size=4),
			Layout(item_list[4], name="a", size=4),
			Layout(item_list[5], name="a", size=4),
			Layout(item_list[6], name="a", size=4),
			Layout(item_list[7], name="a", size=10)
		)

		# return layout
		return layout


	# internally processes a button press
	def _process_press_button(self, button):
		# perform action depending on what button was pressed
		if button == 0:
			self.selected_item = self.selected_item - 1
			if self.selected_item < 0: self.selected_item = self.items -1
			self.display_changed = True
		if button == 1:
			self.selected_item = self.selected_item + 1
			if self.selected_item == self.items: self.selected_item = 0
			self.display_changed = True
		if button == 6:
			self.uarm.start_laser()
			self.arduino.wait_run_command("S_L R1 1")


	# internally processes a button release
	def _process_release_button(self, button):
		if button == 6:
			self.uarm.stop_laser()
			self.arduino.wait_run_command("S_L R1 0")


	# called when a change in the self.button_states array was detected
	def _process_buttons(self):
		# go through all button states and process the changes if neccessary
		for i in range(self.buttons):
			if self.button_states[i] != self.button_states_old[i]:
				if self.button_states[i] == 1: self._process_press_button(i)
				else: self._process_release_button(i)


	# thread main method
	# checks, if the display should be updated
	# if it should, or 2 seconds have passed, recreate it's contents
	# that way it does not update too often, while still keeping information about CPU,
	#  RAM, network or temperature up to date
	def run(self):
		with Live(self._generate_layout(), refresh_per_second=10) as live:
			while True:
				time.sleep(0.1)

				# check if a button was pressed
				if self.buttons_changed:
					self._process_buttons()
					self.buttons_changed = False

				# check if the display should be updated
				if self.display_changed or self.display_timer == 20:
					live.update(self._generate_layout())
					self.display_timer = 0
					self.display_changed = False

				self.display_timer = self.display_timer + 1


# class to retrieve system information
class SystemInfo:
	# returns a string containing the cpu usage in percent
	# a color depending on the value gets applied
	def get_cpu_usage() -> str:
		usage = psutil.cpu_percent()
		if usage < 50: return "[green]{}%[/green]".format(usage)
		elif usage < 70: return "[yellow]{}%[/yellow]".format(usage)
		else: return "[red]{}%[/red]".format(usage)

	# returns a string containing the cpu speed
	def get_cpu_freq() -> str:
		freq_current = psutil.cpu_freq()[0]
		freq_max = psutil.cpu_freq()[2]
		return "[green]{}MHz[/green] / [green]{}MHz[/green]".format(freq_current, freq_max)


	# returns a string containing the cpu temperature
	# a color depending on the value gets applied
	# TODO: do the same thing with psutil to achieve consistency
	def get_cpu_temp() -> str:
		temp = float(subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"]).decode('UTF-8')) / 1000
		if temp < 50: return "[green]{}°C[/green]".format(temp)
		elif temp < 70: return "[yellow]{}°C[/yellow]".format(temp)
		elif temp < 100: return "[red]{}°C[/red]".format(temp)
		else: return "[red]THERMAL MELTDOWN[/red]"


	# returns a string containing the memory usage in percent
	# a color depending on the value gets applied
	def get_memory_usage() -> str:
		usage = psutil.virtual_memory()[2]
		if usage < 40: return "[green]{}%[/green]".format(usage)
		elif usage < 70: return "[yellow]{}%[/yellow]".format(usage)
		else: return "[red]{}%[/red]".format(usage)


	# returns a string containing the size of the physical system memory
	# making a function to do this is actually pretty stupid
	def get_memory_available() -> str:
		return "[green]{}MB[/green]".format(round(psutil.virtual_memory()[0] / 1000000, 2))


	# returns a string containing the amount of memory being used by the system
	# a color depending on the value gets applied
	# TODO: make a similar function returning the amount of memory being used by the program
	def get_memory_used() -> str:
		used = round(psutil.virtual_memory()[3] / 100000, 2)
		usage = psutil.virtual_memory()[2]
		if usage < 40: return "[green]{}MB[/green]".format(used)
		elif usage < 70: return "[yellow]{}MB[/yellow]".format(used)
		else: return "[red]{}MB[/red]".format(used)


	# returns a string containing either "connected" or "Not connected" depending
	#  on whether or not the system is connected to the internet
	# a color depending on the value gets applied
	def get_network_state() -> str:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.settimeout(0.1)
			s.connect(("1.1.1.1", 80))
			return "[green]connected[/green]"			
		except OSError:
			pass
		return "[yellow]Not connected[/yellow]"


	# returns a string containing information about the connection:
	#  wireless
	#  wired
	#  weird (bad joke but actually true)
	# a color depending on the value gets applied
	def get_network_type() -> str:
		network_stats = psutil.net_if_stats()
		for interface in network_stats:
			if interface.startswith("en"):
				if psutil.net_if_stats()[interface].isup: return "[green]wired connection[/green]"
			if interface.startswith("eth"):
				if psutil.net_if_stats()[interface].isup: return "[green]wired connection[/green]"
			if interface.startswith("wl"):
				if psutil.net_if_stats()[interface].isup: return "[green]wireless connection[/green]"
		return "[yellow]Weird[/yellow]"


	# returns the network interface for a given IP
	# https://kbarik.wordpress.com/2020/01/16/get-ip-address-mac-address-and-network-interface-name-using-python-os-independent/
	def get_active_network_interface_name(ipv4Address):
		if ipv4Address != "":
			nics = psutil.net_if_addrs()
			netInterfaceName = [i for i in nics for j in nics[i] if j.address==ipv4Address and j.family==socket.AF_INET][0]
			return netInterfaceName
		return ""


	# returns the system's IP
	# https://kbarik.wordpress.com/2020/01/16/get-ip-address-mac-address-and-network-interface-name-using-python-os-independent/
	def get_ip():
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(("1.1.1.1", 80))
			ip = s.getsockname()[0]
			s.close()
		except OSError:
			return ""
		return ip


	# returns the mac adress of a network interface
	# https://kbarik.wordpress.com/2020/01/16/get-ip-address-mac-address-and-network-interface-name-using-python-os-independent/
	def get_mac(netInterfaceName) -> str:
		if netInterfaceName != "":
			nics = psutil.net_if_addrs()
			macAddress = ([j.address for i in nics for j in nics[i] if i==netInterfaceName and j.family==psutil.AF_LINK])[0]
			return macAddress.replace('-',':')
		return ""
