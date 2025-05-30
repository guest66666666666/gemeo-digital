import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ========== CONFIGURAÇÕES ==========

# Substitua pela sua chave da OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configurações para conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)
sheet = client.open("gemeo_digital").sheet1

# ========== INTERFACE ==========

st.title("👤 Gêmeo Digital - Protótipo v1")

st.subheader("1️⃣ Mensagem recebida")
mensagem_recebida = st.text_area("Cole aqui a mensagem recebida", height=150)

if st.button("Gerar resposta como 'eu'"):
    if mensagem_recebida.strip() == "":
        st.warning("Por favor, insira uma mensagem primeiro.")
    else:
        with st.spinner("Gerando resposta..."):
            prompt = f"Você é {st.secrets['persona_nome']}, responda essa mensagem de forma coerente com seu estilo, valores e histórico:\n\n{mensagem_recebida}"
            resposta_ia = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )["choices"][0]["message"]["content"]

        st.subheader("2️⃣ Resposta da IA (simulando você)")
        st.text_area("Resposta da IA", value=resposta_ia, height=200, key="resposta_ia")

        st.subheader("3️⃣ Avaliação da resposta")
        nota = st.slider("Nota para a resposta da IA (0-10)", 0, 10, 5)
        resposta_real = st.text_area("Sua resposta real à mensagem", height=150)
        justificativa = st.text_area("Por que a resposta da IA não foi adequada?", height=100)

        if st.button("Salvar e treinar modelo"):
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            sheet.append_row([data_atual, mensagem_recebida, resposta_ia, nota, resposta_real, justificativa])
            st.success("Interação salva com sucesso!")
