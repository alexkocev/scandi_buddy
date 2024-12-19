import streamlit as st

st.header("🙋")


try:
    first_name = st.session_state['user_info']['name'].split(" ")[0]
    st.write(f"Hello {first_name},")
except:
    st.write(f"Hello,")
    
    
st.write(f"Welcome to ScandiBudy, your new assistant at ScandiWeb 🚀")


st.write("")
st.write("")
st.write("")

st.write(f"Need help or want to give a feedback? Drop a message at alexandre.kocev@scandiweb.com")

