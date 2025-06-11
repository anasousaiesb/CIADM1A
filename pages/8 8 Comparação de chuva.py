import streamlit as st
import pandas as pd

# Título do aplicativo
st.title("Análise de Dados Climáticos")

# Upload do arquivo
uploaded_file = st.file_uploader("Faça upload do arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Arquivo carregado com sucesso!")
        
        # Mostrar as primeiras linhas
        st.write("Visualização dos dados:")
        st.dataframe(df.head())
        
        # Aqui você pode continuar com sua análise...
        
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.warning("Por favor, faça upload de um arquivo CSV")
