#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "./lib"))
import datetime
import logging
import urllib
import urllib.request
import json
from flask import Flask
from utilities import local_path, split_text_to_lines, get_day, get_date_based_folder_name
from drivers import driver_it8951
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from network import network
from convert import convert
from restart import Restart
from state import state

selfpath = local_path("")
picdir = "{}{}".format(selfpath, 'media')
fontdir = local_path("fonts")

logging.basicConfig(level=logging.INFO)
link_template = 'https://cdn.newseum.org/dfp/pdf{}/{}.pdf'

font36 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 36)
font24 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 24)
font18 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 18)
font16 = ImageFont.truetype(os.path.join(fontdir, 'times.ttf'), 16)

def mkdir(path):
    os.system('mkdir -p {}'.format(path))

def day_path():
    return "{}/{}".format(picdir,get_date_based_folder_name())

def ensure_day_path():
    mkdir(
        day_path()
    )

def download_front_page(paper, force = False):
    day = get_day()
    dest_folder = "{}/{}".format(picdir,get_date_based_folder_name())
    
    ensure_day_path()

    download_output_file = "{}/{}-{}.pdf".format(dest_folder, paper, day)
    # local_path('{}-{}.pdf'.format(paper, day))   
    link = link_template.format(day, paper)
    
    return network.download_file(link, download_output_file, force)

def convert_image_to_bmp(source_file, display_height, display_width, fill = True):
    logging.info("Rendering to e-Ink.")
    dest_file = source_file.replace(".pdf", ".bmp").replace(".jpg", ".bmp")
    exit_code = convert.resize(source_file, dest_file, display_height, display_width, fill)
    if (exit_code == 0):
        logging.info("Rendered: %s", dest_file)
        return dest_file
    else:
        return False

def center_text(draw, font, text, top, display_height, display_width):
    text_width, _text_height = draw.textsize(text, font)
    position = ((display_height-text_width)/2,top)
    draw.text(position, text, font=font, fill=0)
    # return img

def fixup_text(text):
    return text.replace("&rdquo;", "\"").replace("&ldquo;","\"").replace("&mdash;","--")

def draw_text(img, text, content_height, display_height, display_width):
    print("Rendering %s", text)
    img = img.rotate(90, Image.NEAREST, expand = 1)
    draw = ImageDraw.Draw(img)
    max_line_len = 65
    lines = []
    top = content_height
    print("HT", content_height)
    # TODO: Know the original image dimensions so we can properly place the text
    lines = split_text_to_lines(text, max_line_len)
    print(lines)
    for l in lines:
        center_text(draw, font36, l, top, display_height, display_width)
        top = top + 30
    img = img.rotate(270, Image.NEAREST, expand = 1)

    return img

def send_image_to_device(rendered_file, content_height, text, epd):
    logging.info("Preparing to send to device.")
    # epd.Clear()
    time.sleep(1)
    logging.info("Ready to send.")
    time.sleep(5)
    HRYimage = Image.new('1', (epd.height, epd.width), 255)
    HBlackimage = Image.open(rendered_file)
    if (text):
        HBlackimage = draw_text(HBlackimage, fixup_text(text), content_height, epd.height, epd.width)
    logging.info("Image opened.")
    logging.info("Sending to device.")

    left = round((epd.height / 2) - (HBlackimage.height / 2))
    print("Left at ", left)
    # epd.clear()
    epd.draw(0, left, HBlackimage, epd.DISPLAY_UPDATE_MODE_GC16)
    logging.info("Sent to device.")

def render_cartoon(epd):
    with urllib.request.urlopen('https://www.newyorker.com/cartoons/random/randomAPI') as response:
        json_str = response.read()
        data = json.loads(json_str)
        src = data[0]['src']

        dest_file = "{}/{}".format(day_path(), os.path.basename(src))

        filename = network.download_file(src, dest_file)
        
        text = data[0]['caption']
        image = Image.open(filename)
        _width, height = image.size
        
        diff = epd.height / height
        print("Diff", diff)

        rendered_file = convert_image_to_bmp(filename, epd.height, epd.width, False)

        send_image_to_device(rendered_file, round((height * diff)) + 40, text, epd)

def render_paper(paper, epd):
    try: 
        logging.info("Current paper: %s", paper)
        front_page = download_front_page(paper)
        rendered_file = front_page.replace(".pdf", ".bmp")
        if (1 == 1 or os.path.exists(rendered_file) == False):
            rendered_file = convert_image_to_bmp(front_page, epd.height, epd.width, paper != "CARTOON")
            if (rendered_file):
                logging.info("New Front Page Rendered.")
            else:
                # File failed to render, re-try to download since it was probably corrupted
                logging.info("Failed: New Front Page Render. Trying again.")
                front_page = download_front_page(paper, True)
                rendered_file = convert_image_to_bmp(front_page, epd.height, epd.width, paper != "CARTOON")

        if (rendered_file):
            send_image_to_device(rendered_file, epd.width, False, epd)
        else:
            logging.info("Terminal failure: Can't seem to render %s", paper)
    except IOError as err: 
        logging.error("Failed to render paper: {0}".format(err))

def render_next(app_state, epd):
    if (len(app_state.papers) > 0):
        if (app_state.current_index + 1 > len(app_state.papers)):
            app_state.current_index = 0
            app_state.save()
        paper = app_state.papers[app_state.current_index]

        if (paper == "CARTOON"):
            render_cartoon(epd)
        else:
            render_paper(paper, epd)

    else:
        logging.info("No papers in configuration")

def render_battery_low(epd):
    filename = local_path("assets/tesla.bmp")
    send_image_to_device(filename, epd.width, False, epd)
    # shutdown()


def shutdown():
    print("Shutting Down.")
    os.system("sudo shutdown now")

def check_for_command(app_state, epd):
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
            shutdown()
            return False

        if (command == "BATTERY_LOW"):
            render_battery_low(epd)
            shutdown()

        if (command == "UPDATE"):
            print("Updating")
            os.system("bash update.sh")
            return False

        if (command == "RESTART"):
            raise Restart()

        if (command == "RESTART"):
            raise Restart()

        if (command == "RERENDER"):
            app_state.current_index = app_state.current_index - 1
            app_state.next_render = 0
            app_state.save()
            raise Restart()

        if (command == "NEXT"):
            print("Skipping")
            return False
    return True

def cleanup_if_necessary(start_day, current_day): 
    if (start_day != current_day):
        os.system("rm -f *.jpeg *.jpg *.bmp *.pdf *.png")
    return current_day

def save_state(app_state):
    app_state.save(local_path("state.json"))

def load_state():
    return state.load(local_path("state.json"))

def init():
    logging.info("Opening module...")
    epd = driver_it8951.IT8951()
    logging.info("Initializing module...")
    epd.init(False)
    logging.info("Initialized...")
    return epd


def main(continuous = True):
    app_state = load_state()
    
    app_state.current_index = app_state.current_index + 1
    
    epd = init()

    if (app_state.current_index > len(app_state.papers)-1):
        app_state.current_index = 0

    day = get_day()

    try:
        logging.info("NewsFrame v0.1a")
        if (continuous == False):
            render_next(app_state, epd)

            app_state.next_render = time.time() + app_state.interval
            save_state(app_state)
        else:
            while True:
                cleanup_if_necessary(day, get_day())
                should_continue = True
                sleep_interval = 5
                while (should_continue and time.time() < app_state.next_render):
                    should_continue = check_for_command(app_state, epd)
                    time.sleep(sleep_interval)

                render_next(app_state, epd)

                app_state.next_render = time.time() + app_state.interval
                save_state(app_state)

                logging.info("Waiting %d seconds...", app_state.interval)
        
                app_state.current_index = app_state.current_index + 1

    except IOError as e:
        logging.info(e)


network.wait_for_network()


run = True
if (len(sys.argv) > 1 and sys.argv[1] == "--once"):
    main(False)
else:
    while run:
        try:
            main()

        except KeyboardInterrupt:
            logging.info("Sleeping Display")
            logging.info("ctrl + c:")
            # driver_it8951.epdconfig.module_exit()
            run = False
            exit()
        except SystemExit:
            exit(0)
        except Restart:
            logging.info("Restarting...")
        # except:
        #     e = sys.exc_info()[0]
        #     logging.error("An error occured")
        #     logging.error(e)

# epd7in5bc.epdconfig.module_exit()
