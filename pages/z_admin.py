import streamlit as st

if st.session_state.role == "admin":
    st.header("Admin Page")
    st.write("This page is only accessible by admin.")
else:
    st.write("You do not have permission to access this page.")
