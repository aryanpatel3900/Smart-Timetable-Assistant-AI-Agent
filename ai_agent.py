import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def ask_ai(user_query):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_query}]
    )
    return response.choices[0].message.content
