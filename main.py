import pyautogui as pg
from pynput import keyboard
import win32gui, win32con
import re
import time
import json
from dotenv import dotenv_values
import collector
from pymongo_database import MongoTibiaDB


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
    time.sleep(2)
    if pg.locateOnScreen('boots.png'):
        window._handle = last_window
        window.set_foreground()
        return True
    else:
        window._handle = last_window
        window.set_foreground()
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
        time.sleep(2)

def logout():
    pg.press('esc')
    pg.click(x=1902, y=340)
    time.sleep(.5)
    pg.click(x=1030, y=579)
    time.sleep(1)
    pg.click(x=1299, y=729)

def change_character():
    pg.press('esc')
    pg.click(x=1902, y=340)
    time.sleep(.5)
    pg.click(x=1030, y=579)
    time.sleep(2)
    pg.press('down')
    pg.press('enter')
    time.sleep(2)


if __name__ == '__main__':
    import sys
    import logging

    config = dotenv_values('.env')
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s')

    # Connect to MongoDB DataBase
    MongoTibiaDB.initialize()

    listener = keyboard.Listener(on_press=on_press)

    listener.start()

    # focus on tibia window (fullscreen 1920x1080)
    w = WindowMgr()
    w.find_window_wildcard_exact("Tibia")
    w.set_foreground()

    # login
    login(config['PASS'])
    
    closed = False
    server_list = ['Bona', 'Secura', 'Harmonia', 'Inabra', 'Thyrira', 'Antica']
    #loop every 10min
    while not closed:


        for i in range(0, len(server_list)):

            pg.press('a')
            time.sleep(1)
            pg.click(x=786, y=456, button='right')
            time.sleep(1)
            depot = check_depot(w)
            time.sleep(1)
            if not depot:
                if not check_if_logged(w):
                    for _ in range(0, 10):
                        pg.press('esc')
                        time.sleep(.5)
                    time.sleep(1200)
                    login(config['PASS'])
                    if not check_if_logged(w):
                        logging.info('Something is wrong.')
                    else:
                        break
                logging.info("Depot is occupied")
                if i == len(server_list)-1:
                    logout()
                    time.sleep(1)
                    login(config['PASS'])
                else:
                    change_character()
            else:
                pg.click(x=1882, y=501, button='right')
                time.sleep(2)


            # Collect ocr data from market and send to elastic
            with open('item_list.txt') as file:
                item_list = [item.rstrip() for item in file.readlines()]
                file.close()

            for item in item_list:
                try:
                    item_data = find_item_details(w, item, server_list[i])
                except Exception as e:
                    while not check_if_logged(w):
                        for _ in range(0, 10):
                            pg.press('esc')
                            time.sleep(.5)
                        time.sleep(1200)
                        login(config['PASS'])
                        if check_if_logged(w):
                            break
                        else:
                            logging.error('Something is wrong...', exc_info=True)
                            raise Exception(e)
                    if check_if_logged(w):
                        logging.error('Error while collecting ocr data', exc_info=True)
                        collector.grab_image('log.png')
                        raise Exception(e)

            
                # save data to elastic and mongoDB
                response = collector.save_to_elastic(json.dumps(item_data), '192.168.0.201', '9200', config['BASIC_AUTH'], config['BASIC_AUTH'])
                MongoTibiaDB.insert('items', item_data)


                if response.status_code == 200:
                    print('Data sent successfully')
                    logging.info('Data sent successfully')
                else:
                    print('Data could not be send')
                    logging.info(f'Data could not be send with status code {response.status_code}')
                    collector.grab_image('log.png')
                    raise Exception(response.text)
                
            if i == len(server_list)-1:
                logout()
                time.sleep(600)
                login(config['PASS'])
            else:    
                change_character()
            
