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
from seleniumwire import webdriver  # Use seleniumwire instead of selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Inject a simple JavaScript logger to track click events
JS_LOGGER = """
if (!window.clickLog) {
    window.clickLog = [];
}
document.addEventListener('click', function(e) {
    const clickDetails = {
        timestamp: Date.now(),
        x: e.clientX,
        y: e.clientY,
        tagName: e.target.tagName,
        textContent: e.target.textContent.trim().substr(0, 50)  // First 50 chars of text
    };
    window.clickLog.push(clickDetails);
    console.log("[CLICK LOG] ", clickDetails);
});
"""

def inject_logger_script(driver):
    """
    Injects the JS logger into the active browser window.
    """
    driver.execute_script(JS_LOGGER)

def get_click_log(driver):
    """
    Retrieves the click log from the browser.
    """
    return driver.execute_script("return window.clickLog || []")

def main():
    stop_logging = [False]

    def wait_for_user_to_finish():
        """
        Waits until the user presses Enter in the console, then stops the logging loop.
        """
        input("\n** Press Enter (in this console) once you are done with your manual interactions. **\n")
        stop_logging[0] = True

    # Start a separate thread to wait for user input
    input_thread = threading.Thread(target=wait_for_user_to_finish, daemon=True)
    input_thread.start()

    # Configure Selenium Wire options
    seleniumwire_options = {}
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run headless if desired
    driver = webdriver.Chrome(seleniumwire_options=seleniumwire_options, options=chrome_options)

    try:
        # 1. Open the website and inject the logger
        print("Opening https://www.umniah.com/ ...")
        driver.get("https://www.umniah.com/")
        inject_logger_script(driver)
        print("Logger injected to track click events.\n")

        print("===========================================================")
        print("Please manually interact with the website now.")
        print("Only click events and their related network requests will be tracked.")
        print("===========================================================\n")

        # 2. Prepare to log click events and related network requests
        important_requests = []

        while not stop_logging[0]:
            # Get the current click log from the browser
            click_log = get_click_log(driver)

            # Check for new clicks and capture related network requests
            for click_event in click_log:
                # Clear the browser click log after reading
                driver.execute_script("window.clickLog = [];")

                print(f"[USER CLICK] {click_event}")
                click_timestamp = click_event['timestamp']

                # Look for network requests made around the time of the click
                for request in driver.requests:
                    if request.response:
                        # Check if the request occurred within 1 second of the click
                        request_time = request.response.date.timestamp() * 1000  # Convert to ms
                        if abs(request_time - click_timestamp) < 1000:  # 1-second window
                            request_info = {
                                "method": request.method,
                                "url": request.url,
                                "status_code": request.response.status_code,
                                "click_event": click_event,  # Associate this request with the user click
                            }
                            important_requests.append(request_info)
                            print(f"[RELATED REQUEST] {request_info}")

            # Sleep briefly to avoid overloading the loop
            time.sleep(0.5)

    finally:
        # Close the browser
        driver.quit()

    # Write important requests to a JSON file
    filename = "important_click_requests.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(important_requests, f, ensure_ascii=False, indent=2)

    print(f"\nImportant requests saved to {filename}.\n")

if __name__ == "__main__":
    main()
