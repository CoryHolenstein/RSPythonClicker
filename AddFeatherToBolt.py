# Install missing packages if needed
import subprocess
import sys

required = ['pyautogui', 'pygetwindow', 'keyboard']
for package in required:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Imports
import pyautogui
import time
import json
import keyboard
import pygetwindow as gw

# Load config
with open('AddFeatherToBolt.json') as f:
    config = json.load(f)

slot_a = config['slot_a']
slot_b = config['slot_b']
click_delay = config.get('click_delay', 0.05)
runelite_offset = {'x': 0, 'y': 0}

def set_runelite_window():
    global runelite_offset
    title_prefix = config['runelite']['window_title']
    pos = config['runelite']['position']
    size = config['runelite']['size']

    matching_windows = [
        w for w in gw.getWindowsWithTitle(title_prefix) if w.title.startswith(title_prefix)
    ]

    if not matching_windows:
        print(f"No RuneLite window starting with '{title_prefix}' found.")
        return

    win = matching_windows[0]
    try:
        win.moveTo(pos['x'], pos['y'])
        win.resizeTo(size['width'], size['height'])
        runelite_offset = {'x': win.left, 'y': win.top}
        print(f"RuneLite positioned at ({win.left}, {win.top}) with size {win.width}x{win.height}")
    except Exception as e:
        print(f"Failed to adjust RuneLite window: {e}")

def click_slot(slot):
    x = runelite_offset['x'] + slot['x']
    y = runelite_offset['y'] + slot['y']
    pyautogui.click(x, y)

def main():
    set_runelite_window()
    print("Press 'e' to start, 'q' to quit.")

    running = False

    while True:
        if keyboard.is_pressed('e') and not running:
            print("Starting fast A-B-B-A clicks...")
            running = True
            time.sleep(0.5)

        if keyboard.is_pressed('q'):
            print("Quitting.")
            break

        if running:
            click_slot(slot_a)
            time.sleep(click_delay)
            click_slot(slot_b)
            time.sleep(click_delay)
            click_slot(slot_b)
            time.sleep(click_delay)
            click_slot(slot_a)
            time.sleep(click_delay)

if __name__ == '__main__':
    main()
