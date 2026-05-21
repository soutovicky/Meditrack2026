from supabase import create_client
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        st.error("❌ No se encontraron las credenciales de Supabase. Verificá tu archivo .env")
        return None
    return create_client(url, key)

def db():
    """Shortcut para obtener el cliente con el schema meditrack"""
    return get_supabase_client().schema("meditrack")