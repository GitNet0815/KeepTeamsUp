# App to run a tray in windows
# start a cycle of activating ms teams every 3 minutes
import pystray
from pystray import MenuItem as item
import threading
import time
import os
import asyncio
import sys # Import sys for PyInstaller path handling
from PIL import Image, ImageDraw

# Assuming keepTeams.py is in the same directory or accessible via PYTHONPATH
# If keepTeams.py needs to be explicitly included in PyInstaller,
# you'd use --add-data "path/to/keepTeams.py:."
from keepTeams import keepTeamsActive

# Path to the icon file
# For PyInstaller, we need to handle the path differently
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running from PyInstaller bundle, use current script directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Use the helper function for the icon path
ICON_PATH = get_resource_path(os.path.join('assets', 'clock_64.ico'))

# Global flag to control the loop
is_loop_running = False
# Event to signal the background loop (both threading and asyncio parts) to stop
stop_event = threading.Event()

# Function to quit the app
def quit_app(icon, _item):
    print("Exiting application.")
    stop_event.set() # Signal the loop to stop
    icon.stop()

# Function to create tray icon and menu
def create_tray_icon():
    try:
        icon_image = Image.open(ICON_PATH)
    except FileNotFoundError:
        print(f"Error: Icon file not found at {ICON_PATH}. Using a default black image.")
        # Fallback to a simple black image if the icon file is not found
        icon_image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    
    # Create the tray icon with the menu
    icon = pystray.Icon("Teams Automation", icon_image, menu=pystray.Menu(
        item("Start/Stop Loop", toggle_loop),
        item("Quit", quit_app)
    ))
    
    # Run the tray icon (this will keep the tray running)
    icon.run()
    print("Tray Icon is up.")

# Function to start/stop the loop
def toggle_loop(icon, _item):
    global is_loop_running
    if is_loop_running:
        is_loop_running = False
        stop_event.set() # Signal the loop to stop
        print("Loop stopped.")
        # Remove checkmark when loop is stopped
        icon.menu = pystray.Menu(item("Start/Stop Loop", toggle_loop), item("Quit", quit_app))
    else:
        is_loop_running = True
        stop_event.clear() # Clear the stop event for a new run
        print("Loop started.")
        # Start the loop in a new thread. This thread will manage its own asyncio event loop.
        threading.Thread(target=start_loop, daemon=True).start()
        # Add checkmark to indicate the loop is active
        icon.menu = pystray.Menu(item("Start/Stop Loop ✔", toggle_loop), item("Quit", quit_app))
       
# The start_loop function will now manage its own asyncio event loop
def start_loop():
    global is_loop_running
    # Create a new event loop for this thread and set it as the current one
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the main async task until it completes or is cancelled
    try:
        loop.run_until_complete(run_main_async_loop())
    except asyncio.CancelledError:
        print("Async loop cancelled.")
    except Exception as e:
        print(f"Error in async loop: {e}")
    finally:
        # Clean up the loop
        loop.close()
        print("Async loop closed.")

# This is the main asynchronous loop that runs within the dedicated thread
async def run_main_async_loop():
    global is_loop_running
    # Loop as long as it's intended to run and no stop signal is received
    while is_loop_running and not stop_event.is_set():
        await testFunc()
        # Add a small sleep to prevent busy-waiting and allow stop_event to be checked
        if not stop_event.is_set():
            await asyncio.sleep(0.1) # Yield control briefly

async def testFunc():
    global is_loop_running
    # Immediate check to exit if the loop has been signaled to stop
    if not is_loop_running or stop_event.is_set():
        return

    print("Starting a new cycle in testFunc...")

    # Countdown for 180 seconds with updates every 10 seconds for responsiveness
    total_countdown_time = 180
    sleep_interval = 10 
    for i in range(total_countdown_time // sleep_interval):
        if not is_loop_running or stop_event.is_set():
            print("Stopping countdown early.")
            return # Exit if loop should stop
        print(f"Next cycle will start in {total_countdown_time - (i * sleep_interval)} seconds...")
        await asyncio.sleep(sleep_interval) # Use asyncio.sleep

    # Check again before proceeding to automation tasks
    if not is_loop_running or stop_event.is_set():
        return

    # Call automation functions like clicking icons or interacting with Teams
    print("Performing automation tasks...")
    try:
        # Call the keepTeamsActive function to perform the automation tasks
        # Assuming keepTeamsActive is an async function or can be awaited
        await keepTeamsActive()
    except Exception as e:
        print(f"Error occurred in keepTeamsActive: {e}")

    print("Cycle completed. Waiting for the next cycle...")
    
    # The original total_wait_time was 0, meaning no additional wait after automation.
    # If you intend a delay here, change total_wait_time to a positive value.
    total_wait_time = 0 
    for i in range(total_wait_time // sleep_interval): # This loop will not run if total_wait_time is 0
        if not is_loop_running or stop_event.is_set():
            print("Stopping wait early.")
            return # Exit if loop should stop
        await asyncio.sleep(sleep_interval) # Use asyncio.sleep

# Start the tray icon and run it in the background
if __name__ == "__main__":
    # For development, ensure the 'assets' directory and a dummy icon exist
    # PyInstaller will handle bundling these files.
    assets_dir = os.path.join(os.path.abspath("."), 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        try:
            dummy_icon_path = os.path.join(assets_dir, 'clock_64.ico')
            if not os.path.exists(dummy_icon_path):
                img = Image.new('RGB', (64, 64), color=(0, 0, 0))
                img.save(dummy_icon_path)
                print(f"Created a dummy icon at {dummy_icon_path} for development.")
        except Exception as e:
            print(f"Could not create dummy icon: {e}")

    # Start the tray application in a separate thread because pystray.Icon.run() is blocking.
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    # The main thread waits for the tray application thread to finish.
    # This ensures the script doesn't exit prematurely.
    tray_thread.join()
    print("Application finished.")