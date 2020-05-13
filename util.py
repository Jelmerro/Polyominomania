# Welcome to Polyominomania
# See the README.md and github.com/Jelmerro/Polyominomania for more details
# Released into the public domain, see UNLICENSE for details
__license__ = "UNLICENSE"

import os
import platform
import pyglet
import shutil
import subprocess

cur_w = 0
cur_h = 0


def install_font(font):
    if platform.system().lower() == "windows":
        if "WINDIR" in os.environ:
            font_path = os.path.join(os.environ["WINDIR"], "Fonts/")
        else:
            font_path = "C:/Windows/Fonts"
        command = "reg add \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\" \
                  "CurrentVersion\\Fonts\" /v \"Fixedsys Excelsior" \
                  " 3.01 (TrueType)\" /t REG_SZ /d FSEX300.ttf /f"
        error = subprocess.call(command)
        if error:
            print("Please run the program as an admin.")
            return False
        print("Windows does not play nice with fonts.")
        print("Is the automatic installation not working?")
        print("Manually install {}".format(font))
        print("After that start the program with --skip-font.")
    elif platform.system().lower() == "linux":
        font_path = os.path.join(
            os.path.expanduser("~"),
            ".local/share/fonts/")
    elif platform.system().lower() == "darwin":
        font_path = os.path.join(os.path.expanduser("~"), "Library/Fonts/")
    else:
        print("Unsupported OS, please install {} manually.".format(font))
        print("After that start the program with --skip-font.")
        return False
    if not os.path.isdir(font_path):
        os.makedirs(font_path)
    if not os.path.isfile(os.path.join(font_path, "FSEX300.ttf")):
        shutil.copyfile(font, os.path.join(font_path, "FSEX300.ttf"))
    return True


def set_current_res(w, h):
    global cur_w
    global cur_h
    cur_w = w
    cur_h = h


def res(pos_w, pos_h):
    items = {}
    global cur_w
    global cur_h
    des_w = 640
    des_h = 480
    if cur_w / des_w == cur_h / des_h:
        items["wr"] = cur_w / des_w
        items["hr"] = cur_h / des_h
        items["w"] = pos_w * items["wr"]
        items["h"] = pos_h * items["hr"]
    elif cur_w / des_w > cur_h / des_h:
        items["wr"] = cur_h / des_h
        items["hr"] = cur_h / des_h
        items["w"] = ((cur_w - items["wr"] * des_w) / 2) + pos_w * items["wr"]
        items["h"] = pos_h * items["hr"]
    else:
        items["wr"] = cur_w / des_w
        items["hr"] = cur_w / des_w
        items["w"] = pos_w * items["wr"]
        items["h"] = ((cur_h - items["hr"] * des_h) / 2) + pos_h * items["hr"]
    return items


def make_label(name, size, x, y, color, centered, batch):
    position = res(x, y)
    if centered:
        label = pyglet.text.Label(
            name,
            font_name="Fixedsys Excelsior 3.01",
            font_size=int(size*position["wr"]),
            color=color,
            x=int(position["w"]),
            y=int(position["h"]),
            anchor_x="center",
            anchor_y="center",
            batch=batch)
    else:
        label = pyglet.text.Label(
            name,
            font_name="Fixedsys Excelsior 3.01",
            font_size=int(size*position["wr"]),
            color=color,
            x=int(position["w"]),
            y=int(position["h"]),
            batch=batch)
    return label


def split(seq, n):
    current = 0
    limit = 5
    out = [""]
    words = seq.split(" ")
    for word in words:
        if current > limit:
            break
        if len(out[current]) == 0:
            if len(word) > n:
                word = word[:n] + ".."
            out[current] = word
        elif len(out[current]) + len(word) < n:
            out[current] += " " + word
        else:
            if len(word) > n:
                word = word[:n] + ".."
            out.append(word)
            current += 1
    return out
