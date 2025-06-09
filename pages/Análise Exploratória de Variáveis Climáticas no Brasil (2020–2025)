import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo = os.path.join("medias", "medias_mensais_2020_v2.csv")

st.title("Análise Exploratória de Variáveis Climáticas no Brasil (2020–2025)")

try:
    # Ler o arquivo CSV
    df_medias = pd.read_csv(caminho_arquivo)

    # Definir o mês como índice para facilitar a plotagem
    df_medias.set_index('Mês', inplace=True)

    # --- Gráfico de Temperatura ---
    st.subheader("Médias Mensais de Temperatura - 2020")
    fig_temp, ax_temp = plt.subplots(figsize=(10, 5))
    ax_temp.plot(df_medias.index, df_medias['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'], marker='o', label='Temperatura Máxima (°C)', color='red')
    ax_temp.plot(df_medias.index, df_medias['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'], marker='o', linestyle='--', label='Temperatura Mínima (°C)', color='blue')
    ax_temp.set_xlabel('Mês')
    ax_temp.set_ylabel('Temperatura (°C)')
    ax_temp.set_xticks(df_medias.index)
    ax_temp.set_title('Médias Mensais de Temperatura - 2020')
    ax_temp.grid(True)
    ax_temp.legend()
    plt.tight_layout()
    st.pyplot(fig_temp)

    # --- Gráfico de Radiação ---
    st.subheader("Médias Mensais de Radiação Global - 2020")
    fig_rad, ax_rad = plt.subplots(figsize=(10, 5))
    ax_rad.plot(df_medias.index, df_medias['RADIACAO GLOBAL (Kj/m²)'], marker='o', color='orange', label='Radiação Global (Kj/m²)')
    ax_rad.set_xlabel('Mês')
    ax_rad.set_ylabel('Radiação (Kj/m²)')
    ax_rad.set_xticks(df_medias.index)
    ax_rad.set_title('Médias Mensais de Radiação Global - 2020')
    ax_rad.grid(True)
    ax_rad.legend()
    plt.tight_layout()
    st.pyplot(fig_rad)

    # --- Gráfico de Precipitação ---
    st.subheader("Médias Mensais de Precipitação Total - 2020")
    fig_prec, ax_prec = plt.subplots(figsize=(10, 5))
    ax_prec.plot(df_medias.index, df_medias['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], marker='o', color='green', label='Precipitação Total (mm)')
    ax_prec.set_xlabel('Mês')
    ax_prec.set_ylabel('Precipitação (mm)')
    ax_prec.set_xticks(df_medias.index)
    ax_prec.set_title('Médias Mensais de Precipitação Total - 2020')
    ax_prec.grid(True)
    ax_prec.legend()
    plt.tight_layout()
    st.pyplot(fig_prec)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
