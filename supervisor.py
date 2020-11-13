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

logging.basicConfig(level=logging.INFO)

DELTA_MIN=13

# Rely on RTC to keep the time
subprocess.call(["sudo", "hwclock", "--hctosys"])

# Record start time
txt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' -- Started\n'
with open('/home/pi/pi-ink-newsframe/supervisor.log','a') as f:
    f.write(txt)

# This script is started at reboot by cron.
# Since the start is very early in the boot sequence we wait for the i2c-1 device
while not os.path.exists('/dev/i2c-1'):
    time.sleep(0.1)

try:
    pj = pijuice.PiJuice(1, 0x14)
except:
    print("Cannot create pijuice object")
    sys.exit()

percData = pj.status.GetChargeLevel()
message = "Battery Level is currently {}%\n".format(percData['data'])
logging.info(message)

with open('/home/pi/pi-ink-newsframe/supervisor.log','a') as f:
    f.write(message)

if (int(percData['data']) < 25):
  os.system('curl -X POST -d "Body={}" -d "From=+17134899226" -d "To=6463500739" "https://api.twilio.com/2010-04-01/Accounts/ACc204746fc75f13ca53c6647f607bcd31/Messages" -u "ACc204746fc75f13ca53c6647f607bcd31:c1d98da60721e0a354014d79d37b2ec8"'.format(message))

with open('/home/pi/pi-ink-newsframe/supervisor.log','a') as f:
    f.write(txt)


# Do the work
os.system('python3 /home/pi/pi-ink-newsframe/main.py --once')
time.sleep(5)

# Set RTC alarm 5 minutes from now
# RTC is kept in UTC
a={}
a['year'] = 'EVERY_YEAR'
a['month'] = 'EVERY_MONTH'
a['day'] = 'EVERY_DAY'
a['hour'] = 'EVERY_HOUR'
t = datetime.datetime.utcnow()
a['minute'] = (t.minute + DELTA_MIN) % 60
a['second'] = 0
status = pj.rtcAlarm.SetAlarm(a)
if status['error'] != 'NO_ERROR':
    print('Cannot set alarm\n')
    sys.exit()
else:
    print('Alarm set for ' + str(pj.rtcAlarm.GetAlarm()))

# Enable wakeup, otherwise power to the RPi will not be
# applied when the RTC alarm goes off
pj.rtcAlarm.SetWakeupEnabled(True)
time.sleep(0.4)

# PiJuice shuts down power to Rpi after 20 sec from now
# This leaves sufficient time to execute the shutdown sequence
pj.power.SetPowerOff(20)
subprocess.call(["sudo", "poweroff"])