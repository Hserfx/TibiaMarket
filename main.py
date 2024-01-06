import pyautogui as pg
import win32gui
import re
import time
import collector
import requests
import json

url = "http://192.168.0.201:9200/_bulk?pretty"

headers = {
    "Authorization": "eU5ZTzI0d0JFLXhhNzVSVkFqUVU6UTZrYU5wNVNTUE81cEI5WV9jNG1jQQ==",
    "Content-Type": "application/json"
}

class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard,):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)

    def set_focus(self):
        """put focus on the window"""
        win32gui.SetFocus(self._handle)


def find_item_details(item_name):
    """!!!MARKET HAS TO BE OPENED ALREADY
    find item details and gather ocr data to dict
    """
    w = WindowMgr()

    pg.click(x=714, y=744)
    pg.write(item_name)
    time.sleep(1)
    pg.click(x=665, y=494)
    time.sleep(1)
    pg.click(x=1121, y=787)

    w.find_window_wildcard(".*Podgląd w oknie.*")
    w.set_foreground()
    
    return collector.gather_data(item_name)

def save_to_elastic(data):
    basic = requests.auth.HTTPBasicAuth("elastic", "elastic")
    url = "https://192.168.0.201:9200/_bulk?pretty"
    headers = {
        "Authorization": "eU5ZTzI0d0JFLXhhNzVSVkFqUVU6UTZrYU5wNVNTUE81cEI5WV9jNG1jQQ==",
        "Content-Type": "application/x-ndjson"
    }
    
    index_data = '{ "index" : { "_index" : "tibia-marketdata" } }'
    post_data = f"""
    {index_data}
    {data}
    \n
    """
    payload = '\n' + post_data + '\n'

    response = requests.post(url, headers=headers, data=payload, verify=False, auth=basic)
    return response.text


if __name__ == '__main__':

    

    # focus on tibia window (fullscreen 1920x1080)
    tibia_x, tibia_y = pg.locateCenterOnScreen('tibia.png')
    pg.click(tibia_x, tibia_y)

    # login
    pg.write('Eloelo123!')
    time.sleep(1)
    pg.press('enter')
    time.sleep(2)
    pg.press('enter')
    time.sleep(2)

    # Open market (depot in front of you)
    pg.click(x=862, y=388, button='right')
    time.sleep(1)
    pg.click(x=1882, y=501, button='right')
    time.sleep(1)

    

    # Collect ocr data from market
    item_data = find_item_details('tibia coins')
    status = save_to_elastic(item_data)
    print(status)
    
    # Logout fully
    pg.keyDown('alt')
    time.sleep(.2)
    pg.press('tab')
    time.sleep(.2)
    pg.keyUp('alt')
    pg.press('esc')
    pg.press('esc')
    pg.click(x=1902, y=340)
    time.sleep(.5)
    pg.click(x=1030, y=579)
    time.sleep(1)
    pg.click(x=1299, y=729)