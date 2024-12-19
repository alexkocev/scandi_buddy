
# Page 2: AI User Testing
import streamlit as st

st.title("AI User Testing")

# Input KPIs of interest
kpis = st.text_input("Enter KPIs (e.g., Conversion Rate, Session Duration):")

# Upload URLs for analysis
urls = st.text_area("Enter URLs to test (one per line):")

# Button to run AI bot
if st.button("Run AI Test"):
    st.write("AI bot is analyzing the pages...")

    # Display random AI insights
    st.subheader("AI Insights:")
    insights = [
        "Simplify the checkout process to reduce drop-offs.",
        "Optimize images for faster page loads.",
        "Streamline the navigation menu."
    ]
    st.write("\n".join(insights))

    # Compare with human insights
    st.subheader("Human vs. AI Insights:")
    st.write("AI findings closely match human observations.")

