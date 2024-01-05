import pyautogui as pg
import win32gui
import re
import time
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

    def find_window_wildcard(self, wildcard,):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)


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
    
    return collector.gather_data()


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

    # Logout fully
    pg.click(x=1902, y=340)
    time.sleep(.5)
    pg.click(x=1030, y=579)
    time.sleep(.5)
    pg.click(x=1299, y=729)