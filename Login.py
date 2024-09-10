# Login.py
import streamlit as st
from sqlalchemy import create_engine, text
import os

def get_db_engine():
    return create_engine("mysql+pymysql://root:@localhost:3306/streamlit_db")

def check_user(adminName, password):
    query = text("SELECT * FROM admin WHERE adminName = :adminName AND password = :password")
    engine = get_db_engine()
    with engine.connect() as conn:
        result = conn.execute(query, {'adminName': adminName, 'password': password}).fetchone()
        return result is not None

def login_page():
    st.title("Violence Detection Login")
    adminName = st.text_input("Admin", "", key="adminName", placeholder="A d m i n")
    password = st.text_input("Password", "", key="password", type="password", placeholder="Password")
    
    if st.button("Login"):
        if check_user(adminName, password):
            st.session_state['logged_in'] = True
            st.success("Connexion réussie!")
            # Redirect to the DetCamera.py page after successful login
            st.experimental_rerun()
        else:
            st.error("Nom ou mot de passe erroné")

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        # After successful login, redirect to the main detection app (DetCamera.py)
        os.system("streamlit run DetCamera.py")

# Lien vers le fichier CSS
css = open("style.css").read()

# Affichage du CSS
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

if __name__ == '__main__':
    login_page()