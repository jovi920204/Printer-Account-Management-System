import ctypes
import time
import pyautogui as pag
from ctypes import wintypes
import subprocess

user32 = ctypes.WinDLL('user32')
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
FindWindow = user32.FindWindowW
FindWindowEx = user32.FindWindowExW
SendMessage = user32.SendMessageW
endFlag = False

def foreach_window(hwnd, lParam):
    global endFlag
    length = user32.GetWindowTextLengthW(hwnd) + 1
    window_title = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, window_title, length)
    # print(f"Window Title: {window_title.value}")
    if ("列印喜好設定" in window_title.value) or ("Properties" in window_title.value) or ("內容" in window_title.value):
        print(f"Window Title: {window_title.value}")
        # 假設 "確定" 按鈕的 class name 是 "Button"，可以根據需要更改
        button_hwnd = FindWindowEx(hwnd, 0, "Button", None)
        if button_hwnd != 0:
            # 模擬點擊 "確定" 按鈕
            SendMessage(button_hwnd, 0xF5, 0, 0)  # 0xF5 是 "按下" 訊息碼
            time.sleep(0.5)  # 等待操作完成
            endFlag = True
    elif "Adobe" in window_title.value:
        print(f"Window Title: {window_title.value}")
        time.sleep(5)
        subprocess.call("TASKKILL /F /IM Acrobat.exe", shell=True)
        endFlag = True

    return True

def click_ok():
    EnumWindows(EnumWindowsProc(foreach_window), 0)

def run():
    while endFlag == False:
        time.sleep(1)
        click_ok()

if __name__ == '__main__':
    while endFlag == False:
        time.sleep(1)
        click_ok()