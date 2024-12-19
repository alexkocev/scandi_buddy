

#Page 3: Site Suggestions
import streamlit as st

st.title("Site Suggestions")

# Input website URL
website_url = st.text_input("Enter Website URL:")

# Button to scrape and analyze
if st.button("Get Suggestions"):
    st.write(f"Scraping {website_url}...")

    # Display random suggestions
    st.subheader("Improvement Suggestions:")
    suggestions = [
        "Improve mobile responsiveness.",
        "Enhance page load speed.",
        "Add clear call-to-action buttons."
    ]
    st.write("\n".join(suggestions))

