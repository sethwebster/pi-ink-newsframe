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
link_template = 'https://cdn.newseum.org/dfp/pdf{}/{}.pdf'

def download_front_page(paper):
    x = datetime.datetime.now()
    # year = str(x.year)
    # month = str(x.month).zfill(2)
    day = str(x.day).zfill(2)
    download_output_file = os.path.join(selfpath, '{}-{}.pdf'.format(paper, day))

    if (os.path.exists(download_output_file) == False):
        link = link_template.format(day, paper)
        os.system("wget {}".format(link))
        os.rename("{}.pdf".format(paper), download_output_file)
        time.sleep(1)

    return download_output_file

def render_image_to_ink(source_file):
    logging.info("Rendering to e-Ink.")
    dest_file = source_file.replace(".pdf", ".bmp")
    os.system("convert {} -resize 528x880\! -rotate -90 -background white -alpha remove {}".format(source_file, dest_file))
    logging.info("Rendered: %s", dest_file)
    return dest_file

def send_image_to_device(rendered_file, epd):
    logging.info("Preparing to send to device.")
    epd.Clear()
    time.sleep(1)
    logging.info("Ready to send.")
    time.sleep(5)
    HBlackimage = Image.open(rendered_file)
    logging.info("Image opened.")
    HRYimage = Image.new('1', (epd7in5b_V3.EPD_WIDTH, epd7in5b_V3.EPD_HEIGHT), 255)
    logging.info("Sending to device.")
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    logging.info("Sent to device.")

def set_last_paper(index):
    filename = os.path.join(selfpath, 'last-paper.dat')
    file = open("last-paper.dat","w")
    file.write(index)
    file.close()

def get_last_paper():
    try:
        filename = os.path.join(selfpath, 'last-paper.dat')
        if (os.path.exists(filename) == False):
            return 0
        file = open("last-paper.dat", "r")
        dat = file.readlines()
        return int(dat[0])
    except:
        return 0


papers = [
    "NY_NYT",
    "WSJ",
    "NY_NYP",
    "IL_CT",
    "DC_WP",
    "CA_LAT",
    "TX_HC",
    "CA_SFC",
    "AZ_ADS"
]

def main():
    paper_index = get_last_paper() + 1
    if (paper_index > len(papers)):
        paper_index = 0
    delay = 900
    try:

        logging.info("New York Times e-Frame")
        logging.info("Opening module...")
        epd = epd7in5b_V3.EPD()
        logging.info("Initializing module...")
        epd.init()
        while True:
            paper = papers[paper_index]
            set_last_paper(str(paper_index))
            logging.info("Will render %s", paper)
            x = datetime.datetime.now()
            year = str(x.year)
            month = str(x.month).zfill(2)
            day = str(x.day).zfill(2)

            front_page = download_front_page(paper)
            rendered_file = front_page.replace(".pdf", ".bmp")
            new_render = False
            # if (os.path.exists(download_output_file) == False):
            #     logging.info("Downloading %s to %s", link, download_output_file)
            #     urllib.request.urlretrieve(link, download_output_file)
            # else:
            #     logging.info("Today's front page already downloaded.")

            if (os.path.exists(rendered_file) == False):
                rendered_file = render_image_to_ink(front_page)
                new_render = True
                logging.info("New Front Page Rendered.")
            else:
                logging.info("{} front page already rendered.".format(paper))

            tries = 0
            sent = False
            while sent == False and tries < 3:
                tries = tries + 1
                try:
                    send_image_to_device(rendered_file, epd)
                    sent = True
                except IOError as e:
                    logging.info(e)

            # logging.info("Sleeping display.")
            # epd.sleep()
            # logging.info("Sleeping.")


            logging.info("Waiting %d seconds...", delay)
            time.sleep(delay)
            paper_index = paper_index + 1

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("Sleeping Display")
        epd.sleep()
        logging.info("ctrl + c:")
        epd7in5bc.epdconfig.module_exit()
        exit()

while True:
    main()
    epd7in5bc.epdconfig.module_exit()
