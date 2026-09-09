
import streamlit as st

# Acessando a senha cadastrada nos Secrets
senha_correta = st.secrets["credentials"]["senha_app"]

# Exemplo simples de verificação de acesso
senha_digitada = st.text_input("Digite a senha de acesso:", type="password")

if senha_digitada:
    if senha_digitada == senha_correta:
        st.success("Acesso liberado!")
        # Seu código do app aqui
    else:
        st.error("Senha incorreta.")