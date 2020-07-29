#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime
import logging
import urllib.request

selfpath = os.path.dirname(os.path.realpath(__file__))
picdir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.INFO)

link_template = 'https://static01.nyt.com/images/{}/{}/{}/nytfrontpage/scan.pdf'
delay = 1750
try:
    epd = epd7in5b_V3.EPD()
    
    logging.info("New York Times e-Frame")
    while True:
        
        x = datetime.datetime.now()
        year = str(x.year)
        month = str(x.month).zfill(2)
        day = str(x.day).zfill(2)

        link = link_template.format(year, month, day)

        download_output_file = os.path.join(selfpath, 'scan-download-{}-{}-{}.pdf'.format(year, month, day))
        download_render_file = os.path.join(selfpath, 'scan-render-{}-{}-{}.bmp'.format(year, month, day))
        new_render = False
        if (os.path.exists(download_output_file) == False):
            logging.info("Downloading %s to %s", link, download_output_file)
            urllib.request.urlretrieve(link, download_output_file)
        else:
            logging.info("Today's front page already downloaded.")

        if (os.path.exists(download_render_file) == False):
            logging.info("Rendering to e-Ink.")

            os.system("convert {} -resize 528x880\! -rotate -90 {}".format(download_output_file, download_render_file))
            new_render = True
            logging.info("New Front Page Rendered.")
        else: 
            logging.info("Today's front page already rendered.")
            
        if new_render:
            logging.info("Sending to device.")
            epd.init()  
            epd.Clear()
            time.sleep(1)
            HBlackimage = Image.open(download_render_file)
            HRYimage = Image.new('1', (epd7in5b_V3.EPD_WIDTH, epd7in5b_V3.EPD_HEIGHT), 255)
            epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
            logging.info("Sent to device.")
            
            logging.info("Sleeping.")
            epd.sleep()
        
        
        time.sleep(delay)
            
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("Sleeping Display")
    epd.sleep()   
    logging.info("ctrl + c:")
    epd7in5bc.epdconfig.module_exit()
    exit()
