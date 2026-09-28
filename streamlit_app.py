import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Create A Cookbook",
    layout="wide",
    initial_sidebar_state='expanded',

)

enter_url = st.Page('Pages/URL_input.py', title="Enter a URL")
cookbook_page = st.Page('Pages/cookbook.py', title="Cookbook")

pg = st.navigation([enter_url, cookbook_page])
st.set_page_config(page_title= "Your Personal Cookbook")
pg.run()
