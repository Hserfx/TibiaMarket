import cv2
import easyocr
import matplotlib.pyplot as plt
from PIL import ImageGrab
from datetime import datetime
import json


def grab_image(path, bbox=None):
    """makes screenshoot, saving it and returns a NumPy array"""

    img = ImageGrab.grab(all_screens=True)
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(path)

    return cv2.imread(path)


def get_time():
    """returns local time"""

    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def gather_data(item_name = None, server_name = None):
    reader = easyocr.Reader(["en"], gpu=False)
    sell_text = reader.readtext(grab_image('sell_offers.png', bbox=(1020, 280, 1200, 330)))
    buy_text = reader.readtext(grab_image('buy_offers.png', bbox=(1020, 650, 1200, 700)))
    time = get_time()
    
    if not sell_text:
        sell_offer = ''
    else:
        sell_offer = int(sell_text[0][1].replace(',', '').replace('k', '000').replace(' ', ''))

    if not buy_text:
        buy_text = ''
    else:
        buy_offer = int(buy_text[0][1].replace(',', '').replace('k', '000').replace(' ', ''))

    
    return json.dumps({"buy_offer": buy_offer,
            "sell_offer": sell_offer,
            "item_name": item_name,
            "server_name": server_name,
            "time": time})


