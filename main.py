

import streamlit as st
from streamlit_google_auth import Authenticate
import json
import time
from PIL import Image


secrets_path = "./secrets.json"
with open(secrets_path, "r") as f:
    secrets = json.load(f)
CLAUDE_KEY = secrets["CLAUDE_KEY"]



# Set a consistent favicon and page title for all pages
img=Image.open("images/icon_app.png")

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


# def get_role(email):
    # return users.get(email, None)
    

authenticator = Authenticate(
    secret_credentials_path = 'google_credentials.json',
    cookie_name='cookie_name',
    cookie_key='cookie_key',
    # redirect_uri = 'http://localhost:8501',
    redirect_uri = 'https://scandi-buddy-578201479770.europe-west1.run.app'
    #
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


# Define pages and navigation items
page_1 = st.Page(
    "pages/dashboard_analysis.py",
    title="Dashboard Analysis",
    icon=":material/bar_chart:",
    default=False
)
page_2 = st.Page(
    "pages/tracking_report.py",
    title="Tracking Report",
    icon=":material/route:",
    default=False
)
page_3 = st.Page(
    "pages/dataLayer_QA.py",
    title="dataLayer QA",
    icon=":material/apps:",
    default=False
)

page_4 = st.Page(
    "pages/GTM_container_setup.py",
    title="GTM Container",
    icon=":material/equalizer:",
    default=False
)




page_5 = st.Page(
    "pages/ai_website_improvement_suggestions.py",
    title="Website Suggestions 🚧",
    icon=":material/lightbulb:",  # Representing suggestions or ideas
    default=False
)
page_6 = st.Page(
    "pages/dashboard_generator.py",
    title="Dashboard Generator 🚧",
    icon=":material/apps:",  # Representing tools or dashboards
    default=False
)
page_7 = st.Page(
    "pages/dashboard_description_creation.py",
    title="Dashboard Description 🚧",
    icon=":material/text_snippet:",  # Representing content creation
    default=False
)
page_8 = st.Page(
    "pages/data_benchmarking.py",
    title="Data Benchmarking 🚧",
    icon=":material/equalizer:",  # Representing comparisons and benchmarks
    default=False
)
page_9 = st.Page(
    "pages/domain_explorer.py",
    title="Domain Explorer 🚧",
    icon=":material/search:",  # Representing exploration
    default=False
)
page_10 = st.Page(
    "pages/monitoring_system.py",
    title="System Monitoring 🚧",
    icon=":material/autorenew:",  # Representing observation
    default=False
)

page_11 = st.Page(
    "pages/ai_user_testing.py",
    title="AI User Testing 🚧",
    icon=":material/robot:",  # Representing AI testing
    default=False
)




home = st.Page(
    "pages/z_home.py",
    title="Home",
    icon=":material/home:",
    default=(st.session_state.role in ["user", "admin"])
)

admin = st.Page(
    "pages/z_admin.py",
    title="Admin Controls",
    icon=":material/key:",
)

logout_page = st.Page(logout, 
                      title="Log out", 
                      icon=":material/logout:")

# Display app title and logo


st.logo("images/horizontal_app.png", icon_image="images/icon_app.png")

# st.logo("images/SW_logo.jpeg", icon_image="images/SW_logo.jpeg")





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







