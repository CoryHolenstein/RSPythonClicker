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
config_file = "pickpocket_config.json"
MAX_RUNTIME = 5 * 60 * 60  # 5 hours

# Load config
with open(config_file) as f:
    config = json.load(f)

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

def click_exact(x, y):
    final_x = runelite_offset['x'] + x
    final_y = runelite_offset['y'] + y
    pyautogui.moveTo(final_x, final_y, duration=0.1)
    pyautogui.click()
    print(f"Clicked exactly at ({final_x}, {final_y})")

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

def pickpocket_loop():
    global running
    start_time = time.time()
    last_inv_click = start_time
    last_food_click = start_time
    food_index = 0

    pickpocket_spot = config.get("pickpocket_spot", {})
    inventory_click = config.get("inventory_click", {})
    food_slots = config.get("food_slots", [])

    while running:
        current_time = time.time()

        if current_time - start_time >= MAX_RUNTIME:
            print("Max runtime reached. Exiting.")
            running = False
            break

        # Pickpocket 3 times every ~2 seconds (no jitter)
        for _ in range(3):
            click_exact(**pickpocket_spot)
            print(f"Pickpocket clicked exactly at ({pickpocket_spot['x']}, {pickpocket_spot['y']})")
            time.sleep(0.6)

        # Inventory click every 1 minute (no jitter)
        if current_time - last_inv_click >= 60:
            time.sleep(1)
            print("Clicking inventory slot (loot)")
            click_exact(**inventory_click)
            last_inv_click = current_time
            time.sleep(1)

        # Food click every 2 minutes, cycling through food slots (no jitter)
        if current_time - last_food_click >= 120 and food_slots:
            time.sleep(1)
            print(f"Eating food from slot {food_index}")
            click_exact(**food_slots[food_index])
            food_index = (food_index + 1) % len(food_slots)
            last_food_click = current_time

        time.sleep(0.3)


def main():
    global running
    set_runelite_window()
    print("Press 'e' to start, 'q' to quit, 'm' for mouse coordinates.")

    while True:
        if keyboard.is_pressed('e') and not running:
            print("Starting pickpocket bot...")
            running = True
            threading.Thread(target=pickpocket_loop, daemon=True).start()
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
