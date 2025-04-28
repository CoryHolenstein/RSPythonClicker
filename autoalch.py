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
config_file = "diamondcutter_config.json"
MAX_RUNTIME = 18 * 60 * 60  # 5 hours

# Load config
with open(config_file) as f:
    config = json.load(f)

clicks = config.get("clicks", [])
jitter_range = config.get("jitter", 3)

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
    pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.1, 0.2))
    pyautogui.click()
    print(f"Clicked at ({final_x}, {final_y}) with jitter.")

def fidget_mouse_in_client(wait_time):
    start_fidget = time.time()

    # Safety margin to avoid edges (adjust as needed)
    padding = 60

    left = runelite_offset['x'] + padding
    top = runelite_offset['y'] + padding
    right = runelite_offset['x'] + client_size['width'] - padding
    bottom = runelite_offset['y'] + client_size['height'] - padding

    while time.time() - start_fidget < wait_time:
        sleep_time = random.uniform(1.0, 2.5)
        time.sleep(sleep_time)

        try:
            # Random slight offset from current position
            offset_x = random.randint(-115, 125)
            offset_y = random.randint(-100, 153)
            current_x, current_y = pyautogui.position()

            new_x = current_x + offset_x
            new_y = current_y + offset_y

            # Clamp within reduced client bounds
            new_x = max(left, min(new_x, right - 1))
            new_y = max(top, min(new_y, bottom - 1))

            pyautogui.moveTo(new_x, new_y, duration=0.1)
        except Exception as e:
            print(f"Mouse move error: {e}")

def keyboard_activity():
    directions = ['left', 'right']
    interval = config.get("keyboard_activity", {}).get("interval", [45, 90])
    duration_range = config.get("keyboard_activity", {}).get("duration", [2, 4])
    key = random.choice(directions)
    hold_time = random.uniform(*duration_range)
    print(f"Simulating {key.upper()} arrow key for {hold_time:.2f} seconds...")
    keyboard.press(key)
    time.sleep(hold_time)
    keyboard.release(key)


def auto_clicker():
    global running
    start_time = time.time()

    while running:
        if time.time() - start_time >= MAX_RUNTIME:
            print("6 hours reached. Stopping script.")
            running = False
            break

        # Step 1: alch clich
        click_with_jitter(**clicks[0])
        time.sleep(random.uniform(1.0, 1.1))

        # Step 2: select item
        click_with_jitter(**clicks[0])
        time.sleep(random.uniform(2.5, 3))

        keyboard_activity()

        print("Cycle complete. Restarting...\n")

def show_mouse_position():
    print("Move your mouse. Press 'c' to copy coordinates, 'esc' to exit.")
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
    print("Press 'e' to start, 'q' to quit, 'm' for mouse coordinates.")

    while True:
        if keyboard.is_pressed('e') and not running:
            print("Starting auto-clicker...")
            running = True
            threading.Thread(target=auto_clicker, daemon=True).start()
            time.sleep(1)

        if keyboard.is_pressed('q'):
            print("Stopping script.")
            running = False
            break

        if keyboard.is_pressed('m'):
            show_mouse_position()
            print("\nBack to main menu. Press 'e' to start, 'q' to quit, 'm' for mouse coordinates.")

        time.sleep(0.1)

if __name__ == "__main__":
    main()
