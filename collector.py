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


def gather_data(item_name):
    reader = easyocr.Reader(["en"], gpu=False)
    text = reader.readtext(grab_image('details.png', bbox=(600, 500, 1100, 900)))
    time = get_time()

    buy_offers = {"Number of Transactions": text[2][1].split(" ")[-1],
                "Highest Price": text[3][1].split(" ")[2].replace(',', ''),
                "Average Price": text[4][1].split(" ")[2].replace(',', ''),
                "Lowest Price": text[5][1].split(" ")[2].replace(',', ''),
                }

    sell_offers = {"Number of Transactions": text[7][1].split(" ")[-1],
                "Highest Price": text[8][1].split(" ")[2].replace(',', ''),
                "Average Price": text[9][1].split(" ")[2].replace(',', ''),
                "Lowest Price": text[10][1].split(" ")[2].replace(',', '')}
    
    return json.dumps({"buy_offers": buy_offers,
            "sell_offers": sell_offers,
            "item_name": item_name,
            "time": time})


    




if __name__ == '__main__':
    pass