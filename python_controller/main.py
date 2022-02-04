#!/usr/bin/python3

import os
import sys
import time
import random

from controller import arduino
from controller import mainframe

os.system("rm -f log.txt")

s = arduino.SerialArduino("/dev/ttyACM0", 9600)
m = mainframe.Mainframe()
m.set_arduino(s)

s.set_mainframe(m)
s.start()

s.block_ready()


s.wait_run_command("S_L G1 1")
time.sleep(1)
s.wait_run_command("S_L G1 0")


m.start()

# sys.exit()


# while True:
# 	r1 = random.randint(0, 1)
# 	r2 = random.randint(0, 1)

# 	command = "S_L"

# 	if r1 == 0: command += " R1"
# 	else: command += " G1"

# 	command += " {}".format(r2)

# 	s.wait_run_command(command)
# 	print(command)

# print("done")
