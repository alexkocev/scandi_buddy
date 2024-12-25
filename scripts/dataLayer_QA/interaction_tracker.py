import sys
import json
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

# Initialize a global list to store interaction data
interaction_data = []

# Save interaction data to a JSON file
def save_to_json(output_path):
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(interaction_data, f, indent=4)

# Function to handle interaction events and log them
def handle_interaction(page, interaction_type, details):
    # Clean up details to only include necessary attributes
    cleaned_details = {
        "selector": details.get("selector"),
        "text": details.get("text"),
        "attributes": {
            key: value for key, value in details.get("attributes", {}).items() if key in ["id", "class", "type", "name", "href", "value"]
        }
    }
    interaction_data.append({
        "timestamp": time.time(),
        "type": interaction_type,
        "details": cleaned_details,
        "url": page.url
    })

# Main script
def main():
    # Check for input arguments
    if len(sys.argv) < 3:
        print("Usage: python interaction_tracker.py <url> <timestamp>")
        sys.exit(1)
    
    url = sys.argv[1]
    timestamp = sys.argv[2]

    # Ensure output directory exists
    output_dir = Path("data/dataLayer_QA/temp_json")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define output file path
    output_path = output_dir / f"interaction_data_{timestamp}.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--remote-debugging-port=9222"])
        context = browser.new_context()

        # Track new pages/windows and attach event listeners
        def on_new_page(new_page):
            if not hasattr(new_page, "_logInteractions_registered"):
                new_page._logInteractions_registered = True  # Mark the page to prevent re-registration
                print(f"New page detected: {new_page.url}")
                new_page.on("domcontentloaded", lambda: print(f"Page loaded: {new_page.url}"))

                # Expose bindings for clicks and input changes
                new_page.expose_binding("logClick", lambda source, event: handle_interaction(new_page, "click", event))
                new_page.expose_binding("logInput", lambda source, event: handle_interaction(new_page, "input", event))

                new_page.evaluate("""
                    document.addEventListener('click', (e) => {
                        const event = {
                            selector: e.target.tagName || null,
                            text: e.target.innerText?.trim() || null,
                            attributes: Array.from(e.target.attributes).reduce((attrs, attr) => {
                                attrs[attr.name] = attr.value;
                                return attrs;
                            }, {})
                        };
                        window.logClick(event);
                    });

                    document.addEventListener('input', (e) => {
                        const event = {
                            selector: e.target.tagName || null,
                            text: e.target.innerText?.trim() || null,
                            attributes: Array.from(e.target.attributes).reduce((attrs, attr) => {
                                attrs[attr.name] = attr.value;
                                return attrs;
                            }, {})
                        };
                        window.logInput(event);
                    });
                """)

        context.on("page", on_new_page)

        # Open the main page and track interactions
        page = context.new_page()
        on_new_page(page)
        try:
            page.goto(url)
            print("Interact with the website. Click and input events will be logged.")
            page.wait_for_timeout(600000)  # Wait for 10 minutes or until manually closed
        except KeyboardInterrupt:
            print("Tracking stopped manually.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Save the interaction data and gracefully close the browser
            save_to_json(output_path)
            try:
                browser.close()
            except Exception as e:
                print(f"Error during browser closure: {e}")

    print(f"Interaction data saved to {output_path}")

if __name__ == "__main__":
    main()