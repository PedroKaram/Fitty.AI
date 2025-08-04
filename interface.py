import streamlit as st
import requests
import uuid
import yaml
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import streamlit_authenticator as sauth

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

pg = config["postgres"]
db_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['dbname']}"
engine = create_engine(db_url)

@st.cache_resource
def load_credentials():
    query = "SELECT username, email, full_name, password_hash FROM users"
    df = pd.read_sql(query, engine)

    credentials = {"usernames": {}}
    for _, row in df.iterrows():
        credentials["usernames"][row["username"]] = {
            "email": row["email"],
            "name": row["full_name"],
            "password": row["password_hash"]
        }
    return credentials

credentials = load_credentials()

authenticator = sauth.Authenticate(
    credentials,
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

st.set_page_config(page_title="Fitty.AI", page_icon=None, layout=None, initial_sidebar_state="collapsed", menu_items=None)

try:
    authenticator.login(location="main")
except Exception as e:
    st.error(e)

if st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
elif st.session_state.get('authentication_status'):
    with st.sidebar:
        authenticator.logout()

    st.markdown("<h1 style='text-align: center;'>Fitty</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Seu assistente nutricional</h3>", unsafe_allow_html=True)

    if "client_id" not in st.session_state:
        st.session_state.client_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    def ask_nutritionist(message):
        url = "http://localhost:5000/chat"
        payload = {
            "client_id": st.session_state.client_id,
            "message": message
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json().get("reply", "Erro ao obter a resposta.")
        return f"Erro: {response.status_code} - {response.text}"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Conte o que você comeu ou faça uma pergunta:")
    if prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        answer = ask_nutritionist(prompt)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
