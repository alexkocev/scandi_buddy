'''
from playwright.sync_api import sync_playwright

def track_interactions():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # Dictionary to store events
        tracked_events = []

        def log_event(event_name, details):
            tracked_events.append({"event": event_name, "details": details})

        def track_page(page):
            # Log clicks
            page.on("click", lambda click: log_event("click", {
                "x": click.client_x,
                "y": click.client_y,
                "target": click.target,
            }))

            # Log navigation
            page.on("framenavigated", lambda frame: log_event("navigation", {
                "url": frame.url
            }))

            # Log console messages
            page.on("console", lambda msg: log_event("console", msg.text))

        # Set up initial page
        page = context.new_page()
        track_page(page)
        
        # Navigate to target URL
        page.goto("https://www.umniah.com/")

        # Handle new pages (e.g., from links opening in new windows)
        context.on("page", lambda new_page: track_page(new_page))

        # Run the browser and interact manually
        input("Press Enter to close the browser...")

        # Print tracked events
        for event in tracked_events:
            print(event)

        # Clean up
        browser.close()

if __name__ == "__main__":
    track_interactions()
'''

















import time
import json
import threading
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def main():
    # Stop logging flag
    stop_logging = [False]

    def wait_for_user_to_finish():
        """
        Wait for the user to press Enter, signaling the end of interactions.
        """
        input("\n** Press Enter (in this console) once you are done with your manual interactions. **\n")
        stop_logging[0] = True

    # Start a thread to wait for the user to finish
    input_thread = threading.Thread(target=wait_for_user_to_finish, daemon=True)
    input_thread.start()

    # Selenium Wire options
    seleniumwire_options = {
        # Uncomment to disable SSL verification (for test sites)
        # "verify_ssl": False
    }

    # Configure Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    chrome_options.add_argument("--start-maximized")  # Maximize browser window

    # Create the Selenium Wire driver
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )

    try:
        # Open the main website
        print("Opening https://www.umniah.com/ ...")
        driver.get("https://www.umniah.com/")

        print("\n===========================================================")
        print("Please interact with the website:")
        print("- Click buttons or links to navigate.")
        print("===========================================================\n")

        # Prepare storage for click-triggered requests
        click_requests = []

        while not stop_logging[0]:
            # Monitor user interactions
            print("\nClick on the browser, then return here to press Enter for the next step.")
            input("Press Enter after clicking an element to capture its requests:\n")

            # Clear old requests to isolate new ones
            driver.requests.clear()

            # Allow time for the network requests to occur after a click
            print("Capturing requests for 3 seconds...")
            time.sleep(3)

            # Gather network requests made during the time window
            for request in driver.requests:
                if request.response:
                    request_info = {
                        "method": request.method,
                        "url": request.url,
                        "status_code": request.response.status_code,
                        "request_headers": dict(request.headers),
                        "response_headers": dict(request.response.headers),
                    }
                    click_requests.append(request_info)

            print(f"Captured {len(click_requests)} requests after the last click.")

    finally:
        # Close the browser
        driver.quit()

    # Write the filtered requests to JSON
    filename = "filtered_click_requests.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(click_requests, f, ensure_ascii=False, indent=2)

    print(f"\nFiltered click-triggered requests saved to {filename}.\n")

if __name__ == "__main__":
    main()
