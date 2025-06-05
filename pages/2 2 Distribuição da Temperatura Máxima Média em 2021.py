import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Análise de Temperatura Máxima Média - Brasil 2021")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Exibir as colunas disponíveis para ajudar a identificar o nome correto
    st.write("Colunas disponíveis no arquivo CSV:", df_unificado.columns.tolist())

    # Suponha que a coluna correta tenha um nome diferente
    nome_coluna_temp_max = st.selectbox("Selecione a coluna de temperatura máxima:", df_unificado.columns)

    # Filtrar apenas o ano de 2021
    df_2021 = df_unificado[df_unificado['Ano'] == 2021]

    # Lista de regiões únicas
    regioes = df_2021['Regiao'].unique()

    # Agrupar por região e mês, calculando a média da temperatura máxima
    df_agrupado = df_2021.groupby(['Regiao', 'Mês'])[nome_coluna_temp_max].mean().reset_index()

    # Encontrar a região com temperatura máxima média mais alta durante o ano
    regiao_mais_quente = df_agrupado.groupby('Regiao')[nome_coluna_temp_max].mean().idxmax()

    # Filtrar apenas os meses de inverno
    meses_inverno = ['Junho', 'Julho', 'Agosto']
    df_inverno = df_agrupado[df_agrupado['Mês'].isin(meses_inverno)]

    # Encontrar a região com temperatura máxima média mais baixa nos meses de inverno
    regiao_mais_fria = df_inverno.groupby('Regiao')[nome_coluna_temp_max].mean().idxmin()

    # Exibir resultados
    st.subheader(f"Região mais quente de 2021: {regiao_mais_quente}")
    st.subheader(f"Região mais fria nos meses de inverno de 2021: {regiao_mais_fria}")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao processar os dados: {e}")
