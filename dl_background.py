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
import matplotlib.font_manager as fontman


FONTS = ['Ariel.ttf', 'sans_serif.ttf', 'verdana.ttf']

def find_font_file(query):
    """
    Use matplotlib font manager to find a system font
    https://stackoverflow.com/questions/15365405/python-finding-ttf-files

    query should full filename e.g. "verdana.ttf"
    """
    matches = filter(lambda path: query in os.path.basename(path), fontman.findSystemFonts())
    return matches

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
    # get rid of nested DIVs
    description_els = filter(lambda el: len(el.findAll('div')) == 0, description_els)
    paragraphs = extract_paragraphs(description_els)


filename_source = '%s/background-source.jpeg' % os.environ['HOME']
filename = '%s/background.jpeg' % os.environ['HOME']

chunk_size = 1024
with open(filename_source, 'wb') as fd:
    for chunk in r.iter_content(chunk_size):
        fd.write(chunk)

img_source = Image.open(filename_source)

# the maximum size of the image scaled into the middle
max_size = (int(w*0.6), int(h*0.4,))
img_source.thumbnail(max_size, Image.ANTIALIAS)

img_w, img_h = img_source.size

img = Image.new('RGBA', (w, h), (0, 0, 0, 255))
offset = ((w - img_w) / 2, (h - img_h) / 2)
img.paste(img_source, offset)

draw = ImageDraw.Draw(img)

font = None
for font_name in FONTS:
    try:
        font_filename = find_font_file(font_name)[0]
        font = ImageFont.truetype(font_filename, 16, encoding='unic')
        break
    except IndexError:
        pass

if font is None:
    raise Exception("Couldn't find a font to use")


y_text = (h + img_h) / 2 + 20

msg = "\n\n".join([textwrap.fill(p, width=textwidth) for p in paragraphs])
line0_width = None

max_width = max([font.getsize(line)[0] for line in msg.splitlines()])

for line in msg.splitlines():
    width, height = font.getsize(line)
    draw.text(((w - max_width) / 2, y_text), line, font=font, fill=(255, 255, 255))
    y_text += height

img.save(filename)
