#!/usr/bin/python3

import os
import sys
import time
import random

from controller import arduino
from controller import mainframe



s = arduino.SerialArduino("/dev/ttyACM0", 9600)
m = mainframe.Mainframe()
m.set_arduino(s)

s.set_mainframe(m)
s.start()
s.block_ready()

m.start()
