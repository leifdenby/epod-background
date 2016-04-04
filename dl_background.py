#!env python
# -*- coding: utf-8 -*-
"""
Script to generate a desktop background image for EPOD with description taken from website

Install with crontab:

        PYTHONPATH=/scratch/local1/leif/local/lib/python2.7/site-packages¬
        
        0 * * * * python /home/zmaw/m300464/bin/dl_desktop.py¬
"""


import os
import re
import textwrap
import types

from PIL import Image, ImageFont, ImageDraw 
import bs4
import requests

def replace_with_newlines(element):
    text = ''
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, types.StringTypes):
            text += elem
        elif elem.name == 'br':
            text += '\n\n'
    return text

def extract_paragraphs(description_els):
    paragraphs = [replace_with_newlines(el).strip() for el in description_els]
    paragraphs = filter(lambda p: len(p) > 0, paragraphs)
    return paragraphs


w = 1920
h = 1200

textwidth = 150

page_html = requests.get("http://epod.usra.edu/blog/").content

soup = bs4.BeautifulSoup(page_html, "lxml")

img_el = soup.find('img', {'src': re.compile(r"http:\/\/epod.*\/.a\/.*")})
img_url = img_el.get('src')

r = requests.get(img_url, stream=True)

description_els = soup.find('div', {'class': 'entry-body'}).findAll('p')
paragraphs = extract_paragraphs(description_els)

if len(paragraphs) == 0:
    description_els = soup.find('div', {'class': 'entry-body'}).findAll('div')
    paragraphs = extract_paragraphs(description_els)

lines = []

for p in paragraphs:
    lines.append(textwrap.fill(p, width=textwidth))

msg = "\n\n".join(lines)


filename_source = '%s/background-source.jpeg' % os.environ['HOME']
filename = '%s/background.jpeg' % os.environ['HOME']

chunk_size = 1024
with open(filename_source, 'wb') as fd:
    for chunk in r.iter_content(chunk_size):
        fd.write(chunk)

img_source = Image.open(filename_source)

# the maximum size of the image scaled into the middle
max_size = (w*0.6, h*0.4,)
img_source.thumbnail(max_size, Image.ANTIALIAS)

img_w, img_h = img_source.size

img = Image.new('RGBA', (w, h), (0, 0, 0, 255))
offset = ((w - img_w) / 2, (h - img_h) / 2)
img.paste(img_source, offset)

draw = ImageDraw.Draw(img)
# font = ImageFont.truetype(<font-file>, <font-size>)
# font = ImageFont.truetype("sans-serif.ttf", 16)
font = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Arial.ttf', 16, encoding='unic')

w_t, h_t = font.getsize(msg)

w_t = 6*textwidth
h_t = 33*msg.count('\n')

draw.text(((w-w_t)/2, h - h_t/2-100), msg,(255,255,255) ,font=font)
img.save(filename)
