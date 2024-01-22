import cv2
import easyocr
import matplotlib.pyplot as plt
from PIL import ImageGrab
from datetime import datetime
import json
import numpy as np

reader = easyocr.Reader(["en"], gpu=False)

def grab_image(path, bbox=None, hsv=False):
    """makes screenshoot, saving it and returns a NumPy array"""

    img = ImageGrab.grab()
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(path)

    img = cv2.imread(path)
    if hsv:
        lower_blue = np.array([120,0,0])
        upper_blue = np.array([255,100,100])
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        mask = cv2.inRange(img, lower_blue, upper_blue)
        img[mask>0]=(255,255,255)
        
    return img


def get_time():
    """returns local time"""

    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def gather_data(item_name = None, server_name = None):
    sell_text = reader.readtext(grab_image('sell_offers.png', bbox=(1020, 180, 1200, 220), hsv=True))
    buy_text = reader.readtext(grab_image('buy_offers.png', bbox=(1020, 550, 1200, 590), hsv=True))
    time = get_time()
    
    if not sell_text:
        sell_offer = ''
    else:
        sell_offer = int(sell_text[0][1].replace(',', '').replace('k', '000').replace(' ', '').replace('.', ''))

    if not buy_text:
        buy_offer = ''
    else:
        buy_offer = int(buy_text[0][1].replace(',', '').replace('k', '000').replace(' ', '').replace('.', ''))
    
    return json.dumps({"buy_offer": buy_offer,
            "sell_offer": sell_offer,
            "item_name": item_name,
            "server_name": server_name,
            "time": time})


