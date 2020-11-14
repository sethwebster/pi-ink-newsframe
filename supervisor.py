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
logging.info("Newsframe Supervisor Started")
DELTA_MIN = 20
MIN_CHARGE_NOTIFY=100
# Rely on RTC to keep the time
subprocess.call(["sudo", "hwclock", "--hctosys"])

# Record start time
txt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' -- Started\n'
log(txt)
with open('/home/pi/pi-ink-newsframe/supervisor.log', 'a') as f:
    f.write(txt)

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

with open('/home/pi/pi-ink-newsframe/supervisor.log', 'a') as f:
    f.write(message)

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
account_key = os.getenv("TWILIO_ACCOUNT_KEY")
if (int(percData['data']) < MIN_CHARGE_NOTIFY):
    log("Battery level lower than {}% -- notifying via SMS that battery level is {}".format(MIN_CHARGE_NOTIFY, percData['data']))

    curl = 'curl -X POST -d "Body={}" -d "From=+17134899226" -d "To=6463500739" "https://api.twilio.com/2010-04-01/Accounts/{}/Messages" -u "{}:{}"'.format(
        message, account_sid, account_sid, account_key)
    print(curl)
    os.system(curl)

with open('/home/pi/pi-ink-newsframe/supervisor.log', 'a') as f:
    f.write(txt)

log("Starting Render...")
# Do the work
os.system('python3 /home/pi/pi-ink-newsframe/main.py --once')
time.sleep(5)
log("Render Complete")

log("Setting RTC / Alarm")
# Set RTC alarm 5 minutes from now
# RTC is kept in UTC
a = {}
a['year'] = 'EVERY_YEAR'
a['month'] = 'EVERY_MONTH'
a['day'] = 'EVERY_DAY'
a['hour'] = 'EVERY_HOUR'
t = datetime.datetime.utcnow()
a['minute'] = (t.minute + DELTA_MIN) % 60
a['second'] = 0
status = pj.rtcAlarm.SetAlarm(a)
if status['error'] != 'NO_ERROR':
    log('Cannot set alarm\n')
    sys.exit()
else:
    log('Alarm set for ' + str(pj.rtcAlarm.GetAlarm()))

# Enable wakeup, otherwise power to the RPi will not be
# applied when the RTC alarm goes off
pj.rtcAlarm.SetWakeupEnabled(True)
time.sleep(0.4)

# PiJuice shuts down power to Rpi after 20 sec from now
# This leaves sufficient time to execute the shutdown sequence
log("Powering off...")
pj.power.SetPowerOff(20)
subprocess.call(["sudo", "poweroff"])
