# App to run a tray in windows
# start a cycle of activating ms teams every 3 minutes
import pystray
from pystray import MenuItem as item
import threading
import time
import asyncio
from PIL import Image, ImageDraw
from keepTeams import keepTeamsActive

# Global flag to control the loop
is_loop_running = False
# Event to signal the background loop to stop
stop_event = threading.Event()

# Function to quit the app
def quit_app(icon, _item):
    print("Exiting application.")
    stop_event.set() # Signal any running loops to stop
    icon.stop()

# Function to create tray icon and menu
def create_tray_icon():
    icon_image = Image.new('RGB', (64, 64), color=(255, 255, 255))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 0, 0))
    
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
        # Start the loop in a new thread
        threading.Thread(target=start_loop, daemon=True).start()
        # Add checkmark to indicate the loop is active
        icon.menu = pystray.Menu(item("Start/Stop Loop ✔", toggle_loop), item("Quit", quit_app))
       
# Placeholder for the loop (it will be called from the main automation script)
def start_loop():
    global is_loop_running
    # Loop as long as it's intended to run and no stop signal is received
    while is_loop_running and not stop_event.is_set():
        asyncio.run(testFunc())

async def testFunc():
    global is_loop_running
    # Immediate check to exit if the loop has been signaled to stop
    if not is_loop_running or stop_event.is_set():
        return

    print("Starting a new cycle in testFunc...")

    # Countdown for 60 seconds with updates every 1 second for responsiveness
    total_countdown_time = 30
    sleep_interval = 10 
    for i in range(total_countdown_time // sleep_interval):
        if not is_loop_running or stop_event.is_set():
            print("Stopping countdown early.")
            return # Exit if loop should stop
        print(f"Next cycle will start in {total_countdown_time - (i * sleep_interval)} seconds...")
        time.sleep(sleep_interval)

    # Check again before proceeding to automation tasks
    if not is_loop_running or stop_event.is_set():
        return

    # Call automation functions like clicking icons or interacting with Teams
    # Placeholder for actual automation
    print("Performing automation tasks...")
    try:
        # Call the keepTeamsActive function to perform the automation tasks
        task1 = asyncio.create_task(keepTeamsActive())
        await task1
    except Exception as e:
        print(f"Error occurred in keepTeamsActive: {e}")

    print("Cycle completed. Waiting for the next cycle...")
    
    # Wait for 60 seconds before the next cycle, with frequent checks
    total_wait_time = 0
    for i in range(total_wait_time // sleep_interval):
        if not is_loop_running or stop_event.is_set():
            print("Stopping wait early.")
            return # Exit if loop should stop
        time.sleep(sleep_interval)

# Start the tray icon and run it in the background
if __name__ == "__main__":
    # Start the tray application in a separate thread
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    # The main thread waits for the tray application to be closed.
    # This ensures the script doesn't exit prematurely.
    tray_thread.join()
    print("Application finished.")