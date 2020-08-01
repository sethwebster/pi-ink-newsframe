#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime
import logging
import urllib
import urllib.request
import json

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

logging.basicConfig(level=logging.INFO)
link_template = 'https://cdn.newseum.org/dfp/pdf{}/{}.pdf'

font24 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 24)
font18 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 18)
font16 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 16)

papers = [
    "NY_NYT",
    "CARTOON",
    "WSJ",
    "CARTOON",
    "NY_NYP",
    "CARTOON",
    "IL_CT",
    "CARTOON",
    "DC_WP",
    "CARTOON",
    "CA_LAT",
    "CARTOON",
    "TX_HC",
    "CARTOON",
    "CA_SFC",
    "CARTOON",
    "AZ_ADS"
]

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
    if (fill):
        exit_code = os.system("convert {} -resize 528x880\! -background white -gravity center -alpha remove {}".format(source_file, dest_file))
    else:
        exit_code = os.system("convert {} -resize 528x880 -extent 528x880 -background white -gravity center -alpha remove {}".format(source_file, dest_file))
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

def set_last_paper(index):
    logging.info("Saving last paper.")
    filename = local_path('last-paper.dat')
    file = open(filename, "w")
    file.write(index)
    file.close()

def get_last_paper():
    try:
        filename = local_path('last-paper.dat')
        if (os.path.exists(filename) == False):
            return -1
        file = open(filename, "r")
        dat = file.readlines()
        return int(dat[0])
    except:
        return -1

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

def render_next(index, epd): 
    paper = papers[index]
    if (paper == "CARTOON"):
        render_cartoon(epd)

    else:
        render_paper(paper, epd)


def main():
    paper_index = get_last_paper() + 1
    if (paper_index > len(papers)-1):
        paper_index = 0
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

            render_next(paper_index, epd)
            set_last_paper(str(paper_index))

            logging.info("Waiting %d seconds...", delay)
            time.sleep(delay)
            paper_index = paper_index + 1

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
    except:        
        e = sys.exc_info()[0]
        logging.error("An error occured")
        logging.error(e)

epd7in5bc.epdconfig.module_exit()

