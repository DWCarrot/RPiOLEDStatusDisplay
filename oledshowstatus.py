#!/usr/bin/python3

import sys
import os
import re
import time
from PIL import Image, ImageDraw, ImageFont
import board
import busio
import adafruit_ssd1306

def load_font(sz):
    s = os.getenv('OLED_FONT')
    if s:
        font = ImageFont.truetype(s, sz)
    else:
        font = ImageFont.load_default()
    return font



def main(args):
    
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    if len(args) > 0 and args[0] == 'clear':
        exit(0)

    font = load_font(14)

    base_loop = float(15) #30s
    ratio = 60 # 1 ip, 59 info

    oled.fill(0)
    c = 0
    img = None
    while True:
        if c == 0:
            img = show_ip(oled, font, None)
            c = ratio
        else:
            if c % 2 != 0:
                show_info(oled, font, None)
            else:
                img = show_ip(oled, font, img)
            # info
        c -= 1
        time.sleep(base_loop)


def show_ip(oled, font, image):
    if image is None:
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        x = 2
        y = 2
        cy = y
        data = get_inner_ip()
        if len(data) == 0:
            return None
        for (k, v) in data.items():
            text = k + ': ' + v
            (font_width, font_height) = font.getsize(text)
            draw.text((x, cy), text, font=font, fill=255)
            cy += (font_height + y)
    #oled.fill(0)
    oled.image(image)
    oled.show()
    return image

def show_info(oled, font, image):
    if image is None:
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        x = 2
        y = 2
        cy = y
        t1 = 'T:   %.1fC' % (get_temperature())
        t2 = 'CPU: %.2f %.2f %.2f' % get_cpu_average_load()
        t3 = get_memory_usage()
        t3 = ((t3[0] - t3[1] - t3[2] - t3[3]) / 1024, t3[0] / 1024)
        t3 = 'MEM: %d/%dMB' % t3
        for text in (t1, t2, t3):
            (font_width, font_height) = font.getsize(text)
            draw.text((x, cy), text, font=font, fill=255)
            cy += (font_height + y)
    #oled.fill(0)
    oled.image(image)
    oled.show()

def prepare(w, h, font, texts):
    image = Image.new("1", (w, h))
    draw = ImageDraw.Draw(image)
    y = 2
    for text in texts:
        (font_width, font_height) = font.getsize(text)
        draw.text(
            (2, y),
            text,
            font=font,
            fill=255,
        )
        y = y + font_height + 2
    return image
    
def get_temperature():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ifile:
        t = int(ifile.read(5))
        return t / 1000

def get_cpu_average_load():
    with open('/proc/loadavg', 'r') as ifile:
        t = ifile.read()
        t = t.split(' ')
        return (float(t[0]), float(t[1]), float(t[2])) # 1min 5min 15min

def get_memory_usage():
    pattern = re.compile(r'(\S+):\s*(\d+) kB')
    items = ('MemTotal', 'MemFree', 'Buffers', 'Cached')
    with open('/proc/meminfo', 'r') as ifile:
        t = ifile.readline()
        data = dict()
        while t:
            m = pattern.match(t)
            if m is not None:
                item = m.group(1)
                value = int(m.group(2))
                if item in items:
                    data[item] = value
                    if len(data) == len(items):
                        return (data[items[0]], data[items[1]], data[items[2]], data[items[3]])                       
            t = ifile.readline()

def get_inner_ip():
    import getifaddrs
    from socket import AF_INET
    data = dict()
    for t in getifaddrs.getifaddrs():
        if t.name != b'lo' and t.family == AF_INET:
            name = t.name.decode()
            ip = t.addr[0]
            data[name] = ip
    return data

if __name__ == '__main__':
    main(sys.argv[1:])