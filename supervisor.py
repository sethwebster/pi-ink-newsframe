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
import requests #dependency
import json

def log(str):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logstr = dt + " - " + str
    with open('/home/pi/pi-ink-newsframe/supervisor.log', 'a') as f:
        f.write(logstr + "\n")

    logging.info("[NewsFrame]: " + str)

def send_hook(message):
    url = "https://discord.com/api/webhooks/777668325265899530/U93vdjRSkir587zVVz9-jy1SsbtZhcV38msr1g7_4735ktbroJAI6nx675p6VpraQ7Pj"
    data = {}
    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data["content"] = message
    # data["username"] = "custom username"
    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))

logging.basicConfig(level=logging.INFO)
logging.info("Newsframe Supervisor Started")
DELTA_MIN = 45
MIN_CHARGE_NOTIFY=100
# Rely on RTC to keep the time
os.system("sudo sh /home/pi/pi-ink-newsframe/hwclock.sh")
# subprocess.call(["sudo", "hwclock", "--hctosys"])

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
if 'data' in percData:
    message = "Battery Level is currently {}%\n".format(percData['data'])
    logging.info(message)
    if (int(percData['data']) < MIN_CHARGE_NOTIFY):
        log("Battery level lower than {}% -- notifying via SMS that battery level is {}".format(MIN_CHARGE_NOTIFY, percData['data']))
        send_hook(message)
else:
    message = "Error: Could not get battery level."
    logging.info(message)
    print(percData)

with open('/home/pi/pi-ink-newsframe/supervisor.log', 'a') as f:
    f.write(message)


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
    send_hook("Unable to set alarm:{}".format(status['error']))
    sys.exit()
else:
    send_hook('Alarm set for ' + str(pj.rtcAlarm.GetAlarm()))
    log('Alarm set for ' + str(pj.rtcAlarm.GetAlarm()))

# Enable wakeup, otherwise power to the RPi will not be
# applied when the RTC alarm goes off
pj.rtcAlarm.SetWakeupEnabled(True)
time.sleep(0.4)

# PiJuice shuts down power to Rpi after 20 sec from now
# This leaves sufficient time to execute the shutdown sequence
log("Powering off in ~20 seconds")
res = pj.power.SetPowerOff(20)
print(res)
log(str(res))
subprocess.call(["sudo", "poweroff"])
time.sleep(20)
os.system("sudo poweroff now")