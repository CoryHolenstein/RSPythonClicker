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

# Globals
running = False
runelite_offset = {'x': 0, 'y': 0}
client_size = {'width': 765, 'height': 503}
config_file = "nmzclicker2_config.json"
MAX_RUNTIME = 5 * 60 * 60  # 5 hours

# Load config
with open(config_file) as f:
    config = json.load(f)

# Config values
jitter_range = config.get("jitter", 3)
rock_cake_clicks = config.get("rock_cake_clicks", 25)
absorption_sips = config.get("absorption_sips", 20)
rock_cake_interval = config.get("rock_cake_interval", 30)
absorption_interval = config.get("absorption_interval", 45)
overload_interval = config.get("overload_interval", 305)

clicks = config.get("clicks", {})
overload_slots = config.get("overload_slots", [])
absorption_slots = config.get("absorption_slots", [])

mouse_jitter_conf = config.get("mouse_jitter", {})
keyboard_activity_conf = config.get("keyboard_activity", {})

def set_runelite_window():
    global runelite_offset, client_size
    rl_conf = config.get('runelite', {})
    title_prefix = rl_conf.get('window_title', 'RuneLite')
    pos = rl_conf.get('position', {'x': 0, 'y': 0})
    size = rl_conf.get('size', {'width': 765, 'height': 503})
    client_size = size

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
        client_size = {'width': win.width, 'height': win.height}
        print(f"RuneLite positioned at ({win.left}, {win.top}) with size {win.width}x{win.height}")
    except Exception as e:
        print(f"Failed to adjust RuneLite window: {e}")

def click_with_jitter(x, y):
    jitter_x = random.randint(-jitter_range, jitter_range)
    jitter_y = random.randint(-jitter_range, jitter_range)
    final_x = runelite_offset['x'] + x + jitter_x
    final_y = runelite_offset['y'] + y + jitter_y
    pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.05, 0.15))
    pyautogui.click()

def click_multiple(pos_list, count, delay=0.2):
    for _ in range(count):
        slot = random.choice(pos_list)
        click_with_jitter(**slot)
        time.sleep(delay)

def fidget_mouse_thread():
    while running and mouse_jitter_conf.get("enabled", False):
        min_wait, max_wait = mouse_jitter_conf.get("interval", [20, 45])
        time.sleep(random.uniform(min_wait, max_wait))

        padding = 60
        left = runelite_offset['x'] + padding
        top = runelite_offset['y'] + padding
        right = runelite_offset['x'] + client_size['width'] - padding
        bottom = runelite_offset['y'] + client_size['height'] - padding

        offset_x = random.randint(-100, 100)
        offset_y = random.randint(-100, 100)
        current_x, current_y = pyautogui.position()
        new_x = max(left, min(current_x + offset_x, right))
        new_y = max(top, min(current_y + offset_y, bottom))

        pyautogui.moveTo(new_x, new_y, duration=0.1)

def random_keyboard_thread():
    while running and keyboard_activity_conf:
        interval_range = keyboard_activity_conf.get("interval", [20, 50])
        duration_range = keyboard_activity_conf.get("duration", [1, 5])

        time.sleep(random.uniform(*interval_range))

        # Simulate right arrow key to rotate camera
        duration = random.uniform(*duration_range)
        print(f"Rotating camera for {duration:.2f} seconds")
        keyboard.press("right")
        time.sleep(duration)
        keyboard.release("right")

def nmz_clicker():
    global running
    start_time = time.time()

    last_overload = 0
    last_rock_cake = 0
    last_absorption = 0

    print("Starting NMZ loop...")

    # Step 1: First Overload
    click_with_jitter(**random.choice(overload_slots))
    last_overload = time.time()

    # Step 2: Rock cake spam
    for _ in range(rock_cake_clicks):
        click_with_jitter(**clicks["rock_cake"])
        time.sleep(0.1)
    last_rock_cake = time.time()

    # Step 3: Absorption sips
    click_multiple(absorption_slots, absorption_sips, delay=0.2)
    last_absorption = time.time()

    # Start support threads
    if mouse_jitter_conf.get("enabled", False):
        threading.Thread(target=fidget_mouse_thread, daemon=True).start()
    if keyboard_activity_conf:
        threading.Thread(target=random_keyboard_thread, daemon=True).start()

    # Main loop
    while running:
        now = time.time()
        if now - start_time >= MAX_RUNTIME:
            print("Max runtime reached. Exiting.")
            break

        if now - last_overload >= overload_interval:
            print("Drinking overload...")
            click_with_jitter(**random.choice(overload_slots))
            last_overload = now

        if now - last_rock_cake >= rock_cake_interval:
            print("Clicking rock cake...")
            click_with_jitter(**clicks["rock_cake"])
            last_rock_cake = now

        if now - last_absorption >= absorption_interval:
            print("Drinking absorption...")
            click_with_jitter(**random.choice(absorption_slots))
            last_absorption = now

        time.sleep(0.5)

def show_mouse_position():
    print("Move mouse. Press 'c' to copy coords, 'esc' to exit.")
    while True:
        x, y = pyautogui.position()
        print(f"Mouse at ({x}, {y})", end="\r")
        if keyboard.is_pressed('c'):
            adjusted_x = x - runelite_offset['x']
            adjusted_y = y - runelite_offset['y']
            print(f"\nCopied: {{\"x\": {adjusted_x}, \"y\": {adjusted_y}}}")
            time.sleep(0.3)
        if keyboard.is_pressed('esc'):
            break
        time.sleep(0.05)

def main():
    global running
    set_runelite_window()
    print("Press 'e' to start, 'q' to quit, 'm' for mouse position mode.")

    while True:
        if keyboard.is_pressed('e') and not running:
            print("Starting NMZ clicker...")
            running = True
            threading.Thread(target=nmz_clicker, daemon=True).start()
            time.sleep(1)

        if keyboard.is_pressed('q'):
            print("Stopping script.")
            running = False
            break

        if keyboard.is_pressed('m'):
            show_mouse_position()
            print("\nBack to menu. Press 'e' to start, 'q' to quit.")

        time.sleep(0.1)

if __name__ == "__main__":
    main()
