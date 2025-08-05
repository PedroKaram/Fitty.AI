import streamlit as st
import requests
import uuid
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import hashlib

# Configuração inicial do banco
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

pg = config["postgres"]
db_url = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['dbname']}"
engine = create_engine(db_url)

# Configuração visual do Streamlit
st.set_page_config(
    page_title="Fitty.AI", 
    page_icon=None, 
    layout=None, 
    initial_sidebar_state="collapsed", 
    menu_items=None
)

# Inicializa estado de autenticação
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Função para hashear senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- TELA DE LOGIN / CADASTRO ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>Fitty</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Seu assistente nutricional</h3>", unsafe_allow_html=True)

    auth_mode = st.radio("Escolha uma opção:", ("Login", "Cadastrar"), horizontal=True)

    if auth_mode == "Cadastrar":
        st.subheader("Crie sua conta")
        full_name = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        if st.button("Cadastrar"):
            if full_name and email and password:
                hashed_pw = hash_password(password)
                try:
                    with engine.connect() as conn:
                        conn.execute(
                            text("INSERT INTO users (full_name, email, password) VALUES (:full_name, :email, :password)"),
                            {"full_name": full_name, "email": email, "password": hashed_pw}
                        )
                        conn.commit()
                    st.success("Usuário cadastrado com sucesso! Faça login para continuar.")
                except IntegrityError:
                    st.error("Este e-mail já está em uso")
            else:
                st.warning("Preencha todos os campos.")

    elif auth_mode == "Login":
        st.subheader("Acesse sua conta")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if email and password:
                hashed_pw = hash_password(password)
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT * FROM users WHERE email = :email AND password = :password"),
                        {"email": email, "password": hashed_pw}
                    ).fetchone()
                if result:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")
            else:
                st.warning("Preencha todos os campos.")

# --- INTERFACE DO CHAT ---
if st.session_state.authenticated:
    st.success(f"Bem-vindo, {st.session_state.user_email}!")

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
