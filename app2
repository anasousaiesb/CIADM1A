import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Médias Mensais 2020", layout="wide")

st.title("Visualização de Médias Mensais - 2020")
st.markdown(
    """
    Este aplicativo permite visualizar as médias mensais de Temperatura, Radiação Global e Precipitação Total para o ano de 2020.
    Faça o upload do arquivo CSV no formato esperado para visualizar os dados.
    """
)

# Upload de arquivo CSV
uploaded_file = st.file_uploader("Faça upload do arquivo CSV com as médias mensais:", type=["csv"])

if uploaded_file is not None:
    try:
        # Lê o arquivo CSV enviado
        df_medias = pd.read_csv(uploaded_file)

        # Exibe os dados carregados
        st.subheader("Prévia dos dados carregados")
        st.dataframe(df_medias.head())

        # Define o mês como índice se existir a coluna 'Mês'
        if 'Mês' in df_medias.columns:
            df_medias.set_index('Mês', inplace=True)
        else:
            st.warning("A coluna 'Mês' não foi encontrada no arquivo CSV.")

        # Gráficos
        st.subheader("Gráficos de Médias Mensais")

        # --- Gráfico de Temperatura ---
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        try:
            ax1.plot(df_medias.index, df_medias['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'], marker='o', label='Temperatura Máxima (°C)', color='red')
            ax1.plot(df_medias.index, df_medias['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'], marker='o', linestyle='--', label='Temperatura Mínima (°C)', color='blue')
            ax1.set_title('Médias Mensais de Temperatura - 2020')
            ax1.set_xlabel('Mês')
            ax1.set_ylabel('Temperatura (°C)')
            ax1.grid(True)
            ax1.legend()
            st.pyplot(fig1)
        except KeyError as e:
            st.error(f"Coluna não encontrada para o gráfico de Temperatura: {e}")

        # --- Gráfico de Radiação ---
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        try:
            ax2.plot(df_medias.index, df_medias['RADIACAO GLOBAL (Kj/m²)'], marker='o', color='orange', label='Radiação Global (Kj/m²)')
            ax2.set_title('Médias Mensais de Radiação Global - 2020')
            ax2.set_xlabel('Mês')
            ax2.set_ylabel('Radiação (Kj/m²)')
            ax2.grid(True)
            ax2.legend()
            st.pyplot(fig2)
        except KeyError as e:
            st.error(f"Coluna não encontrada para o gráfico de Radiação: {e}")

        # --- Gráfico de Precipitação ---
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        try:
            ax3.plot(df_medias.index, df_medias['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], marker='o', color='green', label='Precipitação Total (mm)')
            ax3.set_title('Médias Mensais de Precipitação Total - 2020')
            ax3.set_xlabel('Mês')
            ax3.set_ylabel('Precipitação (mm)')
            ax3.grid(True)
            ax3.legend()
            st.pyplot(fig3)
        except KeyError as e:
            st.error(f"Coluna não encontrada para o gráfico de Precipitação: {e}")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, faça upload de um arquivo CSV para começar.")
