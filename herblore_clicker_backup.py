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
config_file = "herblore_config.json"
MAX_RUNTIME = 4 * 60 * 60  # 4 hours

# Load config
with open(config_file) as f:
    config = json.load(f)

clicks = config.get("clicks", [])
jitter_range = config.get("jitter", 3)

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

def click_with_jitter(x, y):
    jitter_x = random.randint(-jitter_range, jitter_range)
    jitter_y = random.randint(-jitter_range, jitter_range)
    final_x = runelite_offset['x'] + x + jitter_x
    final_y = runelite_offset['y'] + y + jitter_y
    pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.1, 0.2))
    pyautogui.click()
    print(f"Clicked at ({final_x}, {final_y}) with jitter.")

def auto_clicker():
    global running
    start_time = time.time()

    while running:
        if time.time() - start_time >= MAX_RUNTIME:
            print("4 hours reached. Stopping script.")
            running = False
            break

        # Step 1: First two clicks
        click_with_jitter(**clicks[0])
        click_with_jitter(**clicks[1])
        time.sleep(random.uniform(1, 3))  # Wait after 2nd click

        # Step 2: Start herblore click
        click_with_jitter(**clicks[2])
        time.sleep(random.uniform(20, 30))  # Wait after 3rd click

        # Step 3: Bank click
        click_with_jitter(**clicks[3])
        time.sleep(random.uniform(3, 4))
        # Step 4: New click after opening bank
        click_with_jitter(**clicks[4])
        time.sleep(random.uniform(2, 3))  # Fixed 2s delay after new bank click

        # Step 5: Withdraw Potions
        click_with_jitter(**clicks[5])
        time.sleep(random.uniform(1, 2))

        # Step 6: Withdraw Secondary Item
        click_with_jitter(**clicks[6])
        time.sleep(random.uniform(1, 2))
        # Step 7: Close bank
        click_with_jitter(**clicks[7])

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
            print("\nBack to main menu. Press 's' to start, 'q' to quit, 'm' for mouse coordinates.")

        time.sleep(0.1)


if __name__ == "__main__":
    main()
