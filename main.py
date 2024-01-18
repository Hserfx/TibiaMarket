import pyautogui as pg
from pynput import keyboard
import win32gui, win32con
import re
import time
import json
from dotenv import dotenv_values
import collector


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

    def _window_enum_callback_exact(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows
        and matches with exact window name
        """
        if wildcard == str(win32gui.GetWindowText(hwnd)):
            self._handle = hwnd

    def find_window_wildcard(self, wildcard,):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def find_window_wildcard_exact(self, wildcard,):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback_exact, wildcard)



    def set_foreground(self):
        """put the window in the foreground and maximize it"""
        win32gui.SetForegroundWindow(self._handle)
        win32gui.ShowWindow(self._handle, win32con.SW_MAXIMIZE)



def find_item_details(window, item_name, server_name):
    """!!!MARKET HAS TO BE OPENED ALREADY
    find item details and gather ocr data to dict
    """

    last_window = window._handle
    pg.click(x=757, y=747)
    time.sleep(.1)
    pg.click(x=714, y=744)
    pg.write(item_name)
    time.sleep(1)
    pg.click(x=665, y=494)
    if item_name == 'quill':
        pg.press('down')

    window.find_window_wildcard(".*Podgląd w oknie.*")
    window.set_foreground()

    time.sleep(.3)
    data = collector.gather_data(item_name, server_name)

    window._handle = last_window
    window.set_foreground()

    return data   


def save_to_elastic(data, ip, port):
    """save json data to elasticsearch http://{ip:port}/_bulk?pretty"""

    import requests
    config = dotenv_values('.env')
    url = f"http://{ip}:{port}/_bulk?pretty"

    headers = {
        "Authorization": "eU5ZTzI0d0JFLXhhNzVSVkFqUVU6UTZrYU5wNVNTUE81cEI5WV9jNG1jQQ==",
        "Content-Type": "application/json"
    }

    basic = requests.auth.HTTPBasicAuth(config['BASIC_AUTH'], config['BASIC_AUTH'])
    url = "https://192.168.0.201:9200/_bulk?pretty"
    headers = {
        "Authorization": "eU5ZTzI0d0JFLXhhNzVSVkFqUVU6UTZrYU5wNVNTUE81cEI5WV9jNG1jQQ==",
        "Content-Type": "application/x-ndjson"
    }
    
    index_data = '{ "index" : { "_index" : "tibiamarket-data" } }'
    post_data = f"""
    {index_data}
    {data}
    """
    payload = '\n' + post_data + '\n'

    response = requests.post(url, headers=headers, data=payload, verify=False, auth=basic)
    return response

def check_depot(window):
    """Check if depot is opened"""
    last_window = window._handle
    window.find_window_wildcard(".*Podgląd w oknie.*")
    window.set_foreground()
    time.sleep(1)
    if pg.locateOnScreen('market.png'):
        window._handle = last_window
        window.set_foreground()
        return True
    else:
        return False

def check_if_logged(window):
    """Check if bot is logged in"""
    last_window = window._handle
    window.find_window_wildcard(".*Podgląd w oknie.*")
    window.set_foreground()
    time.sleep(1)
    if pg.locateOnScreen('boots.png'):
        return True
    else:
        return False
    

# program closing safety
def on_press(key):
    """to work app needs to be after his final step,
    waiting for loop to start again"""
    global closed
    try:
        if key.char == ';':
            logging.info('Program closed by user')
            closed = True
            return False
    except AttributeError:
        pass

def login(password):
        pg.write(password)
        time.sleep(1)
        pg.press('enter')
        time.sleep(3)
        pg.press('enter')
        time.sleep(3)


if __name__ == '__main__':
    import sys
    import logging

    config = dotenv_values('.env')
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s')

    listener = keyboard.Listener(on_press=on_press)

    listener.start()

    closed = False
    server_name = 'Bona'
    #loop every 10min
    while not closed:
        # focus on tibia window (fullscreen 1920x1080)
        w = WindowMgr()
        w.find_window_wildcard_exact("Tibia")
        w.set_foreground()

        # login
        login(config['PASS'])


        # Open market (depot in front of you)
        depot = False

        while not depot:
            pg.press('w')
            time.sleep(1)
            pg.click(x=862, y=388, button='right')
            time.sleep(1)
            depot = check_depot(w)
            time.sleep(1)
            if not depot:
                if not check_if_logged(w):
                    for _ in range(0, 10):
                        pg.press('esc')
                        time.sleep(.3)
                        pg.press('enter')
                    login(config['PASS'])
                    if not check_if_logged(w):
                        logging.info('Something is wrong.')
                    else:
                        continue
                logging.info("Depot is occupied")
                time.sleep(10)
            else:
                pg.click(x=1882, y=501, button='right')
                time.sleep(2)


        # Collect ocr data from market and send to elastic
        with open('item_list.txt') as file:
            item_list = [item.rstrip() for item in file.readlines()]

        for item in item_list:
            try:
                item_data = find_item_details(w, item, server_name)
            except Exception as e:
                logging.error('Error while collecting ocr data', exc_info=True)
                collector.grab_image('log.png')
                raise Exception(e)

            response = save_to_elastic(item_data, ip='192.168.0.201', port='9200')

            if response.status_code == 200:
                print('Data sent successfully')
                logging.info('Data sent successfully')
            else:
                print('Data could not be send')
                logging.info(f'Data could not be send with status code {response.status_code}')
                collector.grab_image('log.png')
                raise Exception(response.text)
            
        
        # Logout
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

        # Leave character select
        time.sleep(1)
        pg.click(x=1299, y=729)
        
        # Wait till next login
        time.sleep(600)
        