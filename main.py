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

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)




if __name__ == '__main__':

    w = WindowMgr()
    w.find_window_wildcard('.*Tibia*')
    w.set_foreground()

    pg.write('Eloelo123!')
    time.sleep(1)
    pg.press('enter')
    time.sleep(2)
    pg.press('enter')
    time.sleep(2)
    pg.click(x=862, y=388, button='right')
    time.sleep(1)
    pg.click(x=1882, y=501, button='right')
    time.sleep(1)
    pg.write('tibia coins')
    time.sleep(1)
    pg.click(x=665, y=494)
    time.sleep(1)
    pg.click(x=1121, y=787)

    w.find_window_wildcard(".*Podgląd w oknie.*")
    w.set_foreground()
    data = collector.gather_data()
    print(data)