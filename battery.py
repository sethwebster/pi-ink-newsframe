
#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import print_function

import time
import pijuice
import subprocess
import datetime
import os
import sys
import logging

def log(str):
    logging.info("[NewsFrame]: " + str)

logging.basicConfig(level=logging.INFO)
logging.info("Newsframe Battery Check Started")

# This script is started at reboot by cron.
# Since the start is very early in the boot sequence we wait for the i2c-1 device
log("Waiting for /dev/i2c-1")
while not os.path.exists('/dev/i2c-1'):
    time.sleep(0.1)
log("Wait complete")

log("Initializing PiJuice")

try:
    pj = pijuice.PiJuice(1, 0x14)
except:
    print("Cannot create pijuice object")
    sys.exit()
log("PiJuice Object Initialized")


percData = pj.status.GetChargeLevel()
message = "Battery Level is currently {}%\n".format(percData['data'])
logging.info(message)
