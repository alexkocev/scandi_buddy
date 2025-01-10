import streamlit as st

st.header("🙋")


try:
    first_name = st.session_state['user_info']['name'].split(" ")[0]
    st.write(f"Hello {first_name},")
except:
    st.write(f"Hello,")
    
    
st.write(f"Welcome to ScandiBuddy, your new assistant at ScandiWeb 🚀")


st.write("")
st.write("")
st.write("")

st.write(f"Need help or want to develop a new feature? Drop me a message at alexandre.kocev@scandiweb.com or on Slack @Alexandre Kocev")

