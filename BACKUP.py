# Install missing packages if needed
import subprocess
import sys

required = ['pyautogui', 'keyboard', 'pygetwindow']
for package in required:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Now safely import
import pyautogui
import time
import json
import threading
import keyboard
import pygetwindow as gw
import random

# Load config
with open('config.json') as f:
    config = json.load(f)

first_slots = config['first_slots']
other_slots = config['other_slots']
timing = config['timing']
click_delay = config.get('click_delay', 0.2)
runelite_offset = {'x': 0, 'y': 0}
running = False

# Split other slots
burst_slots = other_slots[:5]
steady_slots = other_slots[5:]

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
    global runelite_offset
    jitter_x = random.randint(-2, 2)
    jitter_y = random.randint(-2, 2)
    x = runelite_offset['x'] + slot['x'] + jitter_x
    y = runelite_offset['y'] + slot['y'] + jitter_y
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.mouseDown()
    time.sleep(0.05)
    pyautogui.mouseUp()
    sleep_time = click_delay + random.uniform(-0.02, 0.1)
    time.sleep(max(0.05, sleep_time))

def click_first_slots():
    while running:
        start_time = time.time()
        print("Clicking first slots...")
        for slot in first_slots:
            click_slot(slot)
            print(f"Clicked first slot at {slot}")
            time.sleep(timing['between_clicks'] + random.uniform(-0.1, 0.2))
        time.sleep(timing['between_slots'] + random.uniform(-0.1, 0.2))
        elapsed = time.time() - start_time
        wait_time = max(0, timing['first_slots_interval'] - elapsed)
        print(f"Waiting {wait_time:.2f}s before next first slot cycle...")
        time.sleep(wait_time)

def burst_click_other_slots():
    print("Performing adjusted burst on first 5 other slots...")
    for slot in burst_slots:
        for i in range(min(timing['clicks_per_slot'], 2)):  # Max 2 clicks per slot
            if not running:
                return
            click_slot(slot)
            print(f"Burst clicked slot {slot} ({i+1}/2)")
            time.sleep(timing['between_clicks'] * 1.5 + random.uniform(-0.1, 0.2))
        time.sleep(timing['between_slots'] * 1.2 + random.uniform(-0.1, 0.2))
    print("Adjusted burst completed.")

def steady_click_other_slots():
    index = 0
    while running:
        if not steady_slots:
            return
        slot = steady_slots[index % len(steady_slots)]
        click_slot(slot)
        print(f"Steady clicked slot {slot} at index {index % len(steady_slots)}")
        index += 1
        time.sleep(timing['other_slots_interval'] + random.uniform(-0.5, 1.0))

def keyboard_activity():
    directions = ['left', 'right']
    interval = config.get("keyboard_activity", {}).get("interval", [45, 90])
    duration_range = config.get("keyboard_activity", {}).get("duration", [2, 4])

    while running:
        wait_time = random.uniform(*interval)
        print(f"Waiting {wait_time:.1f}s before simulating keyboard movement...")
        time.sleep(wait_time)

        if not running:
            break

        key = random.choice(directions)
        hold_time = random.uniform(*duration_range)
        print(f"Simulating {key.upper()} arrow key for {hold_time:.2f} seconds...")
        keyboard.press(key)
        time.sleep(hold_time)
        keyboard.release(key)

def random_mouse_jitter():
    if not config.get("mouse_jitter", {}).get("enabled", True):
        return
    min_interval, max_interval = config["mouse_jitter"].get("interval", [20, 45])
    while running:
        time.sleep(random.uniform(min_interval, max_interval))
        if not running:
            break

        left = runelite_offset['x']
        top = runelite_offset['y']
        width = config['runelite']['size']['width']
        height = config['runelite']['size']['height']

        rand_x = random.randint(left, left + width)
        rand_y = random.randint(top, top + height)
        pyautogui.moveTo(rand_x, rand_y, duration=random.uniform(0.3, 0.7))
        print(f"Moved mouse randomly to ({rand_x}, {rand_y})")

def main():
    global running
    set_runelite_window()
    print("Press 'e' to start, 'q' to quit.")

    start_time = None
    max_runtime = config.get("max_runtime_minutes", 165) * 60

    while True:
        if keyboard.is_pressed('e') and not running:
            print("Starting autoclicker...")
            running = True
            start_time = time.time()

            threading.Thread(target=click_first_slots, daemon=True).start()
            threading.Thread(target=steady_click_other_slots, daemon=True).start()
            threading.Thread(target=burst_click_other_slots, daemon=True).start()
            threading.Thread(target=keyboard_activity, daemon=True).start()
            threading.Thread(target=random_mouse_jitter, daemon=True).start()

            time.sleep(1)

        if running and start_time and (time.time() - start_time >= max_runtime):
            print("165 minutes reached. Stopping autoclicker.")
            running = False
            break

        if keyboard.is_pressed('q'):
            print("Stopping autoclicker.")
            running = False
            break

        time.sleep(0.1)

if __name__ == '__main__':
    main()
