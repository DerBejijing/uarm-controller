import os
import random

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.padding import Padding

import threading
import time


class Mainframe(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.arduino = None
		self.uarm = None
		self.selected_item = 0
		self.display_changed = False
		self.buttons_changed = False
		self.items = 7
		self.buttons = 7

		# initialize array of button states
		self.button_states = [0 for _ in range(self.buttons)]
		self.button_states_old = [0 for _ in range(self.buttons)]


	# setter for arduino reference
	def set_arduino(self, arduino):
		self.arduino = arduino


	# setter for uarm reference
	def set_uarm(self, uarm):
		self.uarm = uarm


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

		os.system("echo {} >> log.txt".format(active_element))

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


		layout["right"].split(
			Layout(Panel("", title="UArm Info", box=box.SQUARE), name="uarm_info"),
			Layout(Panel("", box=box.SQUARE), name="system_info", ratio=3)
		)


		layout["uarm_info"].split_row(
			Layout(Panel(Padding(Align("uArm Speed: [green]100[/green]\nuArm running: [red]no[/red]\nuArm temperature: [green]40 degrees[/green]"), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("LASER enabled: [green]yes[/green]\nLASER active: [red]no[/red]\nLASER power: [green]100%[/green]"), (1, 1)), box=box.SIMPLE))
		)



		layout["system_info"].split(
			Layout(name="system_info_1"),
			Layout(name="system_info_2"),
			Layout(name="system_info_3")
		)

		layout["system_info_1"].split_row(
			Layout(Panel(Padding(Align("CPU usage: [green]28%[/green]\nCPU frequency: [green]2.0GHz[/green]\nCPU temperature: [green]45 degrees[/green]"), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("Memory usage: [green]28%[/green]\nMemory available: [green]4.0GB[/green]\nMemory used: [green]150MB[/green]"), (1, 1)), box=box.SIMPLE))
		)

		layout["system_info_2"].split_row(
			Layout(Panel(Padding(Align("Network state: [red]not connected[/red]\nNetwork name: [red]None[/red]\nNetwork speed: [red]0.0MB/s[/red]"), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("Connection Type: [red]None[/red]\nIP: [red]None[/red]\nMAC: [green]REDACTED[/green]"), (1, 1)), box=box.SIMPLE))
		)

		layout["system_info_3"].split_row(
			Layout(Panel(Padding(Align("SSH server running: [green]yes[/green]\nSSH connected: [red]no[/red]\nSSH account: [green]root[/green]"), (1, 1)), box=box.SIMPLE)),
			Layout(Panel(Padding(Align("Fan speed 1: [green]50%[/green]\nFan speed 2: [green]100%[/green]\nFan speed 3: [green]100%[/green]"), (1, 1)), box=box.SIMPLE))
		)



		# generate a list containing all programs
		item_list = self._generate_list(self.selected_item)

		# insert all programs into the previously generated area
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
		os.system("echo 'process press: {}' >> log.txt".format(button))
		
		# perform action depending on what button was pressed
		if button == 0:
			self.selected_item = self.selected_item - 1
			if self.selected_item < 0: self.selected_item = self.items -1
			self.display_changed = True
		if button == 1:
			self.selected_item = self.selected_item + 1
			if self.selected_item == self.items: self.selected_item = 0
			self.display_changed = True


	# internally processes a button release
	def _process_release_button(self, button):
		pass


	# called when a change in the self.button_states array was detected
	def _process_buttons(self):
		os.system("echo 'buttons: {}' >> log.txt".format(self.button_states))

		# go through all button states and process the changes if neccessary
		for i in range(self.buttons):
			if self.button_states[i] != self.button_states_old[i]:
				if self.button_states[i] == 1: self._process_press_button(i)
				else: self._process_release_button(i)


	# main method
	def run(self):
		with Live(self._generate_layout(), refresh_per_second=10) as live:
			while True:
				time.sleep(0.1)

				# check if a button was pressed
				if self.buttons_changed:
					self._process_buttons()
					self.buttons_changed = False

				# check if the display should be updated
				if self.display_changed:
					os.system("echo 'display updated' >> log.txt")
					live.update(self._generate_layout())
					self.display_changed = False
