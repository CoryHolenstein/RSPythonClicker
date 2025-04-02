# Install missing packages
import subprocess
import sys

for package in ['pyautogui', 'keyboard', 'pygetwindow']:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Imports
import pyautogui
import keyboard
import time
import json
import random
import threading
import pygetwindow as gw
import argparse

# Globals
running = False
runelite_offset = {'x': 0, 'y': 0}
config_file = "agility_config.json"

# CLI input
parser = argparse.ArgumentParser(description="RuneScape Agility Auto Clicker")
parser.add_argument('--course', required=True, help='Name of the course in the config (e.g. Falador, Canifis)')
args = parser.parse_args()
course_name = args.course

# Load config
with open(config_file) as f:
    config = json.load(f)

# Extract course data
course = config.get(course_name)
if not course:
    print(f"Course '{course_name}' not found in config.")
    sys.exit(1)

clicks = course.get("course", [])
marks = course.get("marks_of_grace", [])
click_delay = course.get("click_delay", 5)
jitter_range = course.get("jitter", 3)

# --- Functions ---
def set_runelite_window():
    global runelite_offset
    rl_conf = config.get('runelite', {})
    title_prefix = rl_conf.get('window_title', 'RuneLite')
    pos = rl_conf.get('position', {'x': 0, 'y': 0})
    size = rl_conf.get('size', {'width': 765, 'height': 503})

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

def click_exact(x, y):
    final_x = runelite_offset['x'] + x
    final_y = runelite_offset['y'] + y
    pyautogui.moveTo(final_x, final_y)
    pyautogui.click()
    print(f"Clicked exactly at ({final_x}, {final_y}).")

def click_with_jitter(x, y):
    jitter_x = random.randint(-jitter_range, jitter_range)
    jitter_y = random.randint(-jitter_range, jitter_range)
    final_x = runelite_offset['x'] + x + jitter_x
    final_y = runelite_offset['y'] + y + jitter_y
    pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.1, 0.2))
    pyautogui.click()
    print(f"Clicked at ({final_x}, {final_y}) with jitter.")
    time.sleep(click_delay + random.uniform(-0.5, 0.5))

def click_hide_chat():
    start = config.get("hide_chat")
    if start:
        print(f"Clicking hide chat at {start['x']}, {start['y']}")
        click_exact(start['x'], start['y'])
        
def clickCompass():
    compassClick = course.get("set_camera")
    if compassClick:
        print(f"Clicking compass at {compassClick['x']}, {compassClick['y']}")
        click_exact(compassClick['x'], compassClick['y'])

def click_initial_course_point():
    initial = course.get("initial_click")
    if initial:
        print(f"Clicking initial course point at {initial['x']}, {initial['y']}")
        click_with_jitter(initial['x'], initial['y'])

def autoclicker():
    global running
    step = 0
    while running:
        if step >= len(clicks):
            print("Course complete. Restarting loop...")
            step = 0

        # Click mark of grace (if exists for this step)
        """
        if step < len(marks):
            mark = marks[step]
            if mark:
                print("Clicking mark of grace...")
                click_with_jitter(mark['x'], mark['y'])
        """
        # Click course step
        coord = clicks[step]
        print(f"Clicking course step {step + 1}...")
        click_with_jitter(coord['x'], coord['y'])
        step += 1

def show_mouse_position():
    print("Move your mouse to a position. Press 'c' to copy coordinates, 'esc' to quit.")
    while True:
        x, y = pyautogui.position()
        print(f"Mouse at ({x}, {y})", end="\r")
        if keyboard.is_pressed('c'):
            print(f"Copied: {{\"x\": {x - runelite_offset['x']}, \"y\": {y - runelite_offset['y']}}}")
            time.sleep(0.3)
        if keyboard.is_pressed('esc'):
            break
        time.sleep(0.05)

# --- Main ---
def main():
    global running
    set_runelite_window()
    click_hide_chat()
    clickCompass()
    print(f"Course: {course_name}")
    print("Press 's' to start script, 'q' to quit, 'm' to get mouse positions.")

    while True:
        if keyboard.is_pressed('s') and not running:
            print("Starting agility auto-clicker...")
            running = True
            click_initial_course_point()
            threading.Thread(target=autoclicker, daemon=True).start()
            time.sleep(1)

        if keyboard.is_pressed('q'):
            print("Stopping script.")
            running = False
            break

        if keyboard.is_pressed('m'):
            show_mouse_position()
            print("\nBack to main menu. Press 's' to start, 'q' to quit.")

        time.sleep(0.1)

if __name__ == "__main__":
    main()
