import os
import datetime

def local_path(path):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path)


def split_text_to_lines(text, max_line_len = 65):
    parts = text.split(' ')
    curr_line = ""
    lines = []
    for p in parts:
        if len(curr_line) + len(p) < max_line_len:
            curr_line = curr_line + " " + p
        else:
            lines.append(curr_line)
            curr_line = ""

    if len(curr_line) > 0:
        lines.append(curr_line)

    return lines

def get_day():
    x = datetime.datetime.now()
    return str(x.day) #.zfill(2)
