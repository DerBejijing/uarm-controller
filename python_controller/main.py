#!/usr/bin/python3

import os
import sys
import time
import random

from controller import arduino
from controller import mainframe
from controller import uarm


def main():
	m = mainframe.Mainframe()
	m.init_devices(arduino_port="/dev/ttyACM0", uarm_port="/dev/ttyACM1")
	m.start()

if __name__ == '__main__':
	main()
