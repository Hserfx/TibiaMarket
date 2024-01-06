import cv2
import easyocr
import matplotlib.pyplot as plt
from PIL import ImageGrab
from datetime import datetime
import json


def grab_image():
    img = ImageGrab.grab(all_screens=True)
    cropped_img = img.crop((600, 500, 1100, 900))
    cropped_img.save('details.png')
    return cv2.imread('details.png')

def get_time():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")




def gather_data(item_name):
    reader = easyocr.Reader(["en"], gpu=False)
    text = reader.readtext(grab_image())
    time = get_time()

    buy_offers = {"Number of Transactions": text[2][1].split(" ")[-1],
                "Highest Price": text[3][1].split(" ")[2],
                "Average Price": text[4][1].split(" ")[2],
                "Lowest Price": text[5][1].split(" ")[2],
                }

    sell_offers = {"Number of Transactions": text[7][1].split(" ")[-1],
                "Highest Price": text[8][1].split(" ")[2],
                "Average Price": text[9][1].split(" ")[2],
                "Lowest Price": text[10][1].split(" ")[2]}
    
    return json.dumps({"buy_offers": buy_offers,
            "sell_offers": sell_offers,
            "item_name": item_name,
            "time": time})


    




if __name__ == '__main__':
    pass