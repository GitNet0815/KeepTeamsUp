import pyautogui
import time
import subprocess
import pygetwindow as gw

# Chat 1
chat1 = "D:\\Dev\\Python\\WinTools\\TeamsCaffeine\\chat1.png"
# chat 2
chat2 = "D:\\Dev\\Python\\WinTools\\TeamsCaffeine\\chat1.png"
# Activity 1
activity1 = "D:\\Dev\\Python\\WinTools\\TeamsCaffeine\\activity1.png"
# Activity 2
activity2 = "D:\\Dev\\Python\\WinTools\\TeamsCaffeine\\activity2.png"


# Optional safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Zscaler
progrm = "Teams"



# Function to open MS Teams (if not already open)
def open_teams():
    try:
        # Try to open MS Teams using Windows search
        pyautogui.press('win')  # Press the Windows key
        time.sleep(1)
        pyautogui.write(progrm)  # Type "Teams"
        pyautogui.press('enter')  # Open the app
        print("Opening MS Teams...")
        time.sleep(5)  # Wait for MS Teams to open
    except Exception as e:
        print(f"Error while opening MS Teams: {e}")

# Function to bring MS Teams to the foreground
def bring_teams_to_foreground():
    try:
        open_teams()
        # Get the list of all open windows
        windows = gw.getWindowsWithTitle("Teams")

        if windows:
            # If the Teams window is open, check if it's active
            teams_window = windows[0]  # There should only be one Teams window
            if teams_window.isActive:
                print("MS Teams is already in the foreground.")
            else:
                # If it's not active, bring it to the foreground
                print("Bringing MS Teams to the foreground...")
                teams_window.activate()
                time.sleep(1)  # Give time for the window to activate
        else:
            print("MS Teams is not running. Opening MS Teams...")
            open_teams()
    except Exception as e:
        print(f"Error while bringing Teams to the foreground: {e}")


# Function to click on the 'Chat' icon using image recognition
def click_icon(images, confidence=0.9):
    try:
        # Try each image in the list until one is found
        for image in images:
            button_location = pyautogui.locateOnScreen(image, confidence=confidence)
            if button_location:
                button_center = pyautogui.center(button_location)
                pyautogui.click(button_center)
                print(f"Clicked on the 'Chat' icon using {image}")
                return True
        print(f"Could not find any of the images: {images}")
        return False
    except Exception as e:
        print(f"Error while clicking the 'Chat' icon: {e}")
        return False

# Function to minimize MS Teams window after clicking the "Chat" icon
def minimize_teams_window():
    try:
        # Get the list of open MS Teams windows
        windows = gw.getWindowsWithTitle("Teams")
        if windows:
            teams_window = windows[0]  # There should only be one Teams window
            print("Minimizing MS Teams...")
            teams_window.minimize()
        else:
            print("MS Teams is not open.")
    except Exception as e:
        print(f"Error while minimizing Teams window: {e}")


if __name__ == "__main__":
    while True:  # Loop that runs indefinitely
        print("Starting a new cycle...")

        # Open MS Teams or bring it to the foreground if already open
        bring_teams_to_foreground()

        # Click the 'Chat' icon using either 'chat1.png' or 'chat2.png'
        click_icon([chat1, chat2], confidence=0.9)
        click_icon([activity1, activity2], confidence=0.9)
        click_icon([chat1, chat2], confidence=0.9)

        # Minimize MS Teams window after clicking the Chat icon
        minimize_teams_window()

        print("Cycle completed. Waiting for the next cycle...")
        
        # Wait for the next cycle to start (60 seconds in total)
        # time.sleep(240)  # 240 seconds = 4 minutes
        # Countdown for 240 seconds with updates every 5 seconds
        for remaining in range(240, 0, -5):
            print(f"Next cycle will start in {remaining} seconds...")
            time.sleep(5)  # Wait for 5 seconds before updating the countdown
