#!/bin/sh
sudo modprobe rtc-ds1307 
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device 
sudo hwclock -s
