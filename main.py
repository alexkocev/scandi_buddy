import streamlit as st
from streamlit_google_auth import Authenticate
import json
import time
from PIL import Image
import os
from dotenv import load_dotenv


# Load environment variables from .env file (optional for local dev)
load_dotenv()












# Set a consistent favicon and page title for all pages
images_dir = os.path.join(os.path.dirname(__file__), "images")
img=Image.open(os.path.join(images_dir, "icon_app.png"))
st.set_page_config(page_title="scandiBuddy", page_icon=img, layout="wide")




# Hide the Streamlit footer and menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


if "user_info" not in st.session_state:
    st.session_state["user_info"] = {}

if "connected" not in st.session_state:
    st.session_state["connected"] = False

if "role" not in st.session_state:
    st.session_state["role"] = None
    

    
# Load user roles from config.json
with open('config.json') as f:
    config = json.load(f)
    users = config["users"]
    
def get_role(email):
    # First, check for an exact user match
    if email in users:
        return users[email]

    # If no exact match, check for a domain-level match
    domain = '@' + email.split('@')[-1]
    if domain in users:
        return users[domain]

    # If no match found, return None
    return None




# Get secrets from environment variables
CLAUDE_KEY = os.getenv("CLAUDE_KEY_SW")
if not CLAUDE_KEY:
    st.error("CLAUDE_KEY is not set. Please set it as an environment variable.")
    st.stop()


# Retrieve secrets from environment variables
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET_SCANDIBUDDY")
if not GOOGLE_CLIENT_SECRET:
    st.error("Google OAuth credentials are not set. Please set GOOGLE_CLIENT_SECRET as environment variables.")
    st.stop()



# Construct a credentials dictionary
google_credentials = {        
    "web": {
        "client_id": "268051479638-pgs4n0b9034f0iio3454l1g4m7iv7s3m.apps.googleusercontent.com",
        "project_id": "scandu",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": [
            "http://buddytools.scandiweb.com/",
            "https://buddytools.scandiweb.com/",
            "http://127.0.0.1:8080/",
            'http://localhost:8501/',
            'https://scandi-buddy-578201479770.europe-west1.run.app',
        ]
    }
}

# Write credentials dynamically to a temporary file
with open("temp_google_credentials.json", "w") as temp_file:
    json.dump(google_credentials, temp_file)



authenticator = Authenticate(
    secret_credentials_path = 'temp_google_credentials.json',
    cookie_name='cookie_name',
    cookie_key='cookie_key',
    redirect_uri = 'https://buddytools.scandiweb.com/'
    # redirect_uri = 'http://127.0.0.1:8080/',
    # redirect_uri = 'http://localhost:8501/',
    # redirect_uri = 'https://scandi-buddy-578201479770.europe-west1.run.app',

    
)



# Login event handler
authenticator.check_authentification()














# Create the login/logout functionality
def login():
    authenticator.login()
    if st.session_state.get('connected'):
        email = st.session_state['user_info'].get('email')
        role = get_role(email)
        if role:
            st.session_state.role = role
            st.rerun()

        else:
            st.error("Your email is not registered. Please contact the administrator.")
            st.session_state.role = None
            time.sleep(2)
            logout()  # Automatically log out after showing the error


def logout():
    if st.session_state.get('connected'):
        authenticator.logout()
        st.session_state.role = None
        st.write("You are logged out")
        time.sleep(2)
        st.rerun()



# https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded

app_pages_dir = os.path.join(os.path.dirname(__file__), "app_pages")

# Define pages and navigation items
page_1 = st.Page(
    os.path.join(app_pages_dir, "dashboard_analysis.py"),
    title="Dashboard Analysis",
    icon=":material/bar_chart:",
    default=False
    )
page_2 = st.Page(
    os.path.join(app_pages_dir, "tracking_report.py"),
    title="Tracking Report",
    icon=":material/route:",
    default=False
)
page_3 = st.Page(
    os.path.join(app_pages_dir, "dataLayer_QA.py"),
    title="dataLayer QA",
    icon=":material/apps:",
    default=False
)

page_4 = st.Page(
    os.path.join(app_pages_dir, "GTM_container_setup.py"),
    title="GTM Container",
    icon=":material/equalizer:",
    default=False
)




page_5 = st.Page(
    os.path.join(app_pages_dir, "ai_website_improvement_suggestions.py"),
    title="Website Suggestions 🚧",
    icon=":material/lightbulb:",  # Representing suggestions or ideas
    default=False
)
page_6 = st.Page(
    os.path.join(app_pages_dir, "dashboard_generator.py"),
    title="Dashboard Generator 🚧",
    icon=":material/apps:",  # Representing tools or dashboards
    default=False
)
page_7 = st.Page(
    os.path.join(app_pages_dir, "dashboard_description_creation.py"),
    title="Dashboard Description 🚧",
    icon=":material/text_snippet:",  # Representing content creation
    default=False
)
page_8 = st.Page(
    os.path.join(app_pages_dir, "data_benchmarking.py"),
    title="Data Benchmarking 🚧",
    icon=":material/equalizer:",  # Representing comparisons and benchmarks
    default=False
)
page_9 = st.Page(
    os.path.join(app_pages_dir, "domain_explorer.py"),
    title="Domain Explorer 🚧",
    icon=":material/search:",  # Representing exploration
    default=False
)
page_10 = st.Page(
    os.path.join(app_pages_dir, "monitoring_system.py"),
    title="System Monitoring 🚧",
    icon=":material/autorenew:",  # Representing observation
    default=False
)

page_11 = st.Page(
    os.path.join(app_pages_dir, "ai_user_testing.py"),
    title="AI User Testing 🚧",
    icon=":material/robot:",  # Representing AI testing
    default=False
)




home = st.Page(
    os.path.join(app_pages_dir, "z_home.py"),
    title="Home",
    icon=":material/home:",
    default=(st.session_state.role in ["user", "admin"])
)

admin = st.Page(
    os.path.join(app_pages_dir, "z_admin.py"),
    title="Admin Controls",
    icon=":material/key:",
)

logout_page = st.Page(logout, 
                      title="Log out", 
                      icon=":material/logout:")

# Display app title and logo
st.logo("images/horizontal_app.png", icon_image="images/icon_app.png")




# Define page dictionary for role-based navigation
page_dict = {}

# Populate user-accessible pages
if st.session_state.role in ["user", "admin"]:
    page_dict["User"] = [page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8, page_9, page_10, page_11]

# Create the "Account" group with Home, Admin, and Log Out
navigation_items = {}
if st.session_state.role in ["user", "admin"]:
    # Insert items in desired order
    navigation_items = {
        **page_dict,
        "Account": [home, logout_page],
    }

if st.session_state.role is None:
    navigation_items = {
        "Account": [home, logout_page],
    }


if st.session_state.role == "admin":
    # Insert items in desired order
    navigation_items = {
        **page_dict,
        "Account": [home, admin, logout_page],
    }




# Navigation logic
if len(page_dict) > 0:
    pg = st.navigation(navigation_items)
else:
    pg = st.navigation([st.Page(login)])

pg.run()







# Cleanup: Delete the temporary credentials file (optional for security)
# import os
# os.remove("temp_google_credentials.json")