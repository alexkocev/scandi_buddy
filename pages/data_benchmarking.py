# Page 1: Data Gathering

import streamlit as st
import pandas as pd
import numpy as np

st.title("Data Benchmarking")

# Select data sources
data_sources = st.multiselect(
    "Select Data Sources:",
    ["GA4", "Search Console", "BigQuery", "Magento", "Shopify"]
)

# Select localization
localization = st.selectbox(
    "Select Store Localization:",
    ["North America", "Europe", "Asia", "Australia"]
)

# Button to gather and anonymize data
if st.button("Gather Data"):
    st.write("Data gathered and anonymized successfully!")

    # Display random benchmark KPIs
    st.subheader("Benchmark KPIs:")
    kpis = {
        "Conversion Rate": f"{np.random.uniform(1, 5):.2f}%",
        "Average Order Value": f"${np.random.uniform(50, 200):.2f}",
        "Bounce Rate": f"{np.random.uniform(20, 70):.2f}%"
    }
    st.json(kpis)
