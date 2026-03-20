import streamlit as st
import os
from google import genai

def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        API_KEY = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=API_KEY)
