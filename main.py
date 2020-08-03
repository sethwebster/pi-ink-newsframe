#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime
import logging
import urllib
import urllib.request
import json
from flask import Flask

def local_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

selfpath = local_path("")
picdir = selfpath
fontdir = local_path("fonts")
libdir = local_path("lib")

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from network import network
from convert import convert
from restart import Restart
from state import state

logging.basicConfig(level=logging.INFO)
link_template = 'https://cdn.newseum.org/dfp/pdf{}/{}.pdf'

font24 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 24)
font18 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 18)
font16 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 16)

def get_day():
    x = datetime.datetime.now()
    return str(x.day) #.zfill(2)

def download_file(url, force = False):
    None

def download_front_page(paper, force = False):
    day = get_day()
    download_output_file = local_path('{}-{}.pdf'.format(paper, day))

    if (force and os.path.exists(download_output_file)):
        os.remove(download_output_file)

    if (force or os.path.exists(download_output_file) == False):
        link = link_template.format(day, paper)
        os.system("wget {}".format(link))
        os.rename("{}.pdf".format(paper), download_output_file)
        time.sleep(1)

    return download_output_file

def convert_image_to_bmp(source_file, fill = True):
    logging.info("Rendering to e-Ink.")
    dest_file = source_file.replace(".pdf", ".bmp").replace(".jpg", ".bmp")
    exit_code = convert.resize(source_file, dest_file, fill)
    if (exit_code == 0):
        logging.info("Rendered: %s", dest_file)
        return dest_file
    else:
        return False

def center_text(draw, font, text, top):
    text_width, text_height = draw.textsize(text, font)
    position = ((epd7in5b_V3.EPD_HEIGHT-text_width)/2,top)
    draw.text(position, text,font=font, fill=0)
    # return img

def fixup_text(text):
    return text.replace("&rdquo;", "\"").replace("&ldquo;","\"").replace("&mdash;","--")

def draw_text(img, text, content_height):
    print("Rendering %s", text)
    draw = ImageDraw.Draw(img)
    center_text(draw, font16, text, content_height)
    return img

def send_image_to_device(rendered_file, content_height, text, epd):
    logging.info("Preparing to send to device.")
    # epd.Clear()
    time.sleep(1)
    logging.info("Ready to send.")
    time.sleep(5)
    HRYimage = Image.new('1', (epd7in5b_V3.EPD_HEIGHT, epd7in5b_V3.EPD_WIDTH), 255)
    HBlackimage = Image.open(rendered_file)
    if (text):
        HBlackimage = draw_text(HBlackimage, fixup_text(text), content_height)
    logging.info("Image opened.")
    logging.info("Sending to device.")
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    logging.info("Sent to device.")

def render_cartoon(epd):
    with urllib.request.urlopen('https://www.newyorker.com/cartoons/random/randomAPI') as response:
        json_str = response.read()
        data = json.loads(json_str)
        src = data[0]['src']
        text = data[0]['caption']
        os.system('wget {}'.format(src))
        filename = os.path.basename(src)
        image = Image.open(filename)
        width, height = image.size

        rendered_file = convert_image_to_bmp(filename, False)

        send_image_to_device(rendered_file, height + 40, text, epd)

def render_paper(paper, epd):
    logging.info("Current paper: %s", paper)
    front_page = download_front_page(paper)
    rendered_file = front_page.replace(".pdf", ".bmp")
    if (os.path.exists(rendered_file) == False):
        rendered_file = convert_image_to_bmp(front_page, paper != "CARTOON")
        if (rendered_file):
            logging.info("New Front Page Rendered.")
        else:
            # File failed to render, re-try to download since it was probably corrupted
            logging.info("Failed: New Front Page Render. Trying again.")
            front_page = download_front_page(paper, True)
            rendered_file = convert_image_to_bmp(front_page)

    if (rendered_file):
        send_image_to_device(rendered_file, epd7in5b_V3.EPD_WIDTH, False, epd)
    else:
        logging.info("Terminal failure: Can't seem to render %s", paper)

def render_next(app_state, epd):
    if (len(app_state.papers) > 0):
        paper = app_state.papers[app_state.current_index]
        if (paper == "CARTOON"):
            render_cartoon(epd)

        else:
            render_paper(paper, epd)
    else:
        logging.info("No papers in configuration")

def check_for_command():
    filename = local_path("COMMAND")
    print("Checking for command: {}", filename)
    if os.path.exists(filename):
        file = open(filename, "r")
        dat = file.readlines()
        command = dat[0].strip()
        os.remove(filename)
        
        print ("Command Received: ", command)

        if (command == "STOP"):
            print("Terminating")
            exit(0)
            return False

        if (command == "REBOOT"):
            print("Rebooting")
            os.system("sudo reboot")
            return False

        if (command == "SHUTDOWN"):
            print("Shutting Down.")
            os.system("sudo shutdown now")
            return False

        if (command == "RESTART"):
            raise Restart()

        if (command == "NEXT"):
            print("Skipping")
            return False
    return True

def main():
    app_state = state.load(local_path("state.dat"))
    app_state.current_index = app_state.current_index + 1
    if (app_state.current_index > len(app_state.papers)-1):
        app_state.current_index = 0
    day = get_day()
    delay = 900
    try:

        logging.info("NewsFrame v0.1a")
        logging.info("Opening module...")
        epd = epd7in5b_V3.EPD()
        logging.info("Initializing module...")
        epd.init()
        while True:
            if (get_day() != day):
                # day has changed, clean up
                os.system("rm -f *.jpg")
                os.system("rm -f *.bmp")
                os.system("rm -f *.pdf")
                day = get_day()

            render_next(app_state, epd)
            app_state.save()
            logging.info("Waiting %d seconds...", delay)

            interval = 5
            wait_time = 0
            keep_going = True
            while (keep_going and wait_time < delay):
                keep_going = check_for_command()
                time.sleep(interval)
                wait_time = wait_time + interval
    
            app_state.current_index = app_state.current_index + 1

    except IOError as e:
        logging.info(e)


network.wait_for_network()


run = True
while run:
    try:
        main()

    except KeyboardInterrupt:
        logging.info("Sleeping Display")
        logging.info("ctrl + c:")
        epd7in5b_V3.epdconfig.module_exit()
        run = False
        exit()
    except SystemExit:
        exit(0)
    except Restart:
        logging.info("Restarting...")
    except:
        e = sys.exc_info()[0]
        logging.error("An error occured")
        logging.error(e)

epd7in5bc.epdconfig.module_exit()
