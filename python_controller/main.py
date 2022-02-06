#!/usr/bin/python3

import os
import sys
import time
import random

from controller import arduino
from controller import mainframe
from controller import uarm


def main():
	# These might change
	s = arduino.SerialArduino("/dev/ttyACM0", 9600)
	u = uarm.SerialUarm("/dev/ttyACM1", 115200)

	m = mainframe.Mainframe()
	m.set_arduino(s)
	m.set_uarm(u)

	s.set_mainframe(m)
	s.start()
	s.block_ready()

	m.start()

if __name__ == '__main__':
	main()
