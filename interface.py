import streamlit as st
import requests
import uuid

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
