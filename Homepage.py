import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome! 👋")

# st.sidebar.success("Select a Guide in the side bar.")

st.markdown(
    """
    This site is built to quickly access tuning and tidal information for the J70
    ###
    **👈 Select a Tuning Guide from the sidebar [>]
    (top left on mobile)** 
    ###
  
    ### Want to learn more?
    - Check out the source code [GitHub](https://github.com/jack-rockett/J70_Tuning_Guide)
    
    ### Want to contribute?
    - Watch this space... **Bringing out template and submission form soon**
"""
)