import pyautogui
import time

while True:
    pyautogui.keyDown('right')
    time.sleep(0.3)
    pyautogui.keyUp('right')
    time.sleep(0.1)