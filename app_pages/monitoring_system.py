

# Page 7: Monitoring
import streamlit as st

st.title("Monitoring")

# Select metrics to monitor
metrics = st.multiselect(
    "Select Metrics:",
    ["Revenue", "Conversion Rate", "Page Views", "Add to Cart"]
)

# Set threshold
threshold = st.slider("Set Alert Threshold (%):", 1, 50, 20)

# Button to start monitoring
if st.button("Start Monitoring"):
    st.write("Monitoring started...")

    # Simulate an alert
    st.error("Alert: Revenue difference exceeds 20%!")

