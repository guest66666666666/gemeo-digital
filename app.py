import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import numpy as np
import openai

# ========== CONFIGURAÇÕES ==========

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
sheet_client = gspread.authorize(credentials)
sheet = sheet_client.open("gemeo_digital").sheet1

# OpenAI
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ========== FUNÇÕES AUXILIARES ==========

def embed_text(text):
    """Obtém o embedding do texto usando o modelo da OpenAI"""
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(vec1, vec2):
    """Calcula a similaridade de cosseno entre dois vetores"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

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

            response = openai_client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            resposta_ia = response.choices[0].message.content

        st.subheader("2️⃣ Resposta da IA (simulando você)")
        st.text_area("Resposta da IA", value=resposta_ia, height=200, key="resposta_ia")

        st.subheader("3️⃣ Avaliação da resposta")
        nota = st.slider("Nota para a resposta da IA (0-10)", 0, 10, 5)
        resposta_real = st.text_area("Sua resposta real à mensagem", height=150)
        justificativa = st.text_area("Por que a resposta da IA não foi adequada?", height=100)

        if st.button("Salvar e treinar modelo"):
            if resposta_real.strip() == "":
                st.error("Você precisa preencher sua resposta real para calcular a similaridade.")
            else:
                with st.spinner("Salvando e calculando similaridade..."):
                    try:
                        emb_ia = embed_text(resposta_ia)
                        emb_real = embed_text(resposta_real)
                        similaridade = cosine_similarity(emb_ia, emb_real)
                        similaridade_pct = round(similaridade * 100, 2)
                        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

                        sheet.append_row([
                            data_atual,
                            mensagem_recebida,
                            resposta_ia,
                            nota,
                            resposta_real,
                            justificativa,
                            f"{similaridade_pct}%"
                        ])

                        st.success(f"Interação salva com sucesso! Similaridade: {similaridade_pct}%")
                    except Exception as e:
                        st.error(f"Erro ao salvar ou calcular similaridade: {e}")