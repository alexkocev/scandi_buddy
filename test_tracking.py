import json
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

# Initialize a global list to store interaction data
interaction_data = []

# Save interaction data to a JSON file
def save_to_json():
    output_file = Path("interaction_data.json")
    with output_file.open("w", encoding="utf-8") as f:
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
        page.goto("https://www.umniah.com/")
        print("Interact with the website. Click and input events will be logged.")
        page.wait_for_timeout(600000)  # Wait for 10 minutes or until manually closed
    except KeyboardInterrupt:
        print("Tracking stopped manually.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Save the interaction data and gracefully close the browser
        save_to_json()
        try:
            browser.close()
        except Exception as e:
            print(f"Error during browser closure: {e}")

print("Interaction data saved to interaction_data.json")



















# STREAMLIT

import subprocess
import threading
import json
import os
import time
import streamlit as st

# Globals
output_file = "interaction_data.json"

# Helper function to run the Playwright script
def run_script(url):
    script = f"""
import json
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

interaction_data = []

def save_to_json():
    output_file = Path("{output_file}")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(interaction_data, f, indent=4)

def handle_interaction(page, interaction_type, details):
    cleaned_details = {{
        "selector": details.get("selector"),
        "text": details.get("text"),
        "attributes": {{
            key: value for key, value in details.get("attributes", {{}}).items() if key in ["id", "class", "type", "name", "href", "value"]
        }}
    }}
    interaction_data.append({{
        "timestamp": time.time(),
        "type": interaction_type,
        "details": cleaned_details,
        "url": page.url
    }})

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--remote-debugging-port=9222"])
    context = browser.new_context()

    def on_new_page(new_page):
        if not hasattr(new_page, "_logInteractions_registered"):
            new_page._logInteractions_registered = True
            new_page.on("domcontentloaded", lambda: print(f"Page loaded: {{new_page.url}}"))

            new_page.expose_binding("logClick", lambda source, event: handle_interaction(new_page, "click", event))
            new_page.expose_binding("logInput", lambda source, event: handle_interaction(new_page, "input", event))

            new_page.evaluate('''
                document.addEventListener('click', (e) => {{
                    const event = {{
                        selector: e.target.tagName || null,
                        text: e.target.innerText?.trim() || null,
                        attributes: Array.from(e.target.attributes).reduce((attrs, attr) => {{
                            attrs[attr.name] = attr.value;
                            return attrs;
                        }}, {{}});
                    }};
                    window.logClick(event);
                }});

                document.addEventListener('input', (e) => {{
                    const event = {{
                        selector: e.target.tagName || null,
                        text: e.target.innerText?.trim() || null,
                        attributes: Array.from(e.target.attributes).reduce((attrs, attr) => {{
                            attrs[attr.name] = attr.value;
                            return attrs;
                        }}, {{}});
                    }};
                    window.logInput(event);
                }});
            ''')

    context.on("page", on_new_page)

    page = context.new_page()
    on_new_page(page)
    try:
        page.goto("{url}")
        page.wait_for_timeout(600000)
    except KeyboardInterrupt:
        print("Tracking stopped manually.")
    finally:
        save_to_json()
        browser.close()

print("Interaction data saved to {output_file}")
"""
    return subprocess.Popen(
        ["python", "-c", script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

# Initialize session state for process
if "process" not in st.session_state:
    st.session_state.process = None

# Streamlit UI
st.title("Interaction Tracker")

url = st.text_input("Enter URL:", placeholder="https://example.com")
if st.button("Launch"):
    if url:
        st.session_state.process = run_script(url)
        st.success("Tracking started! Switch to the browser window.")
    else:
        st.error("Please enter a valid URL.")

if st.button("Stop"):
    if st.session_state.process:
        st.session_state.process.terminate()
        st.session_state.process = None
        time.sleep(2)  # Allow time for cleanup
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
                st.code(json.dumps(data, indent=4), language="json")
        else:
            st.warning("No interaction data found.")
    else:
        st.warning("No process is currently running.")




#Here’s how to adapt your interaction_tracker.py and dataLayer_QA.py to incorporate unique JSON file naming based on timestamps, fetched from dataLayer_QA.py, and store them in the data/dataLayer_QA/temp_json directory.