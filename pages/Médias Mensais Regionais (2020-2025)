import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Médias Mensais Regionais (2020-2025) - Facetado por Região e Variável")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Calcular a média da temperatura
    df_unificado['Temperatura Média (°C)'] = (
        df_unificado['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
        df_unificado['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
    ) / 2

    # Lista de regiões e anos únicas
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Variáveis a serem plotadas
    variaveis = {
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }

    # Seleção interativa da variável
    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    import numpy as np
    from matplotlib.cm import get_cmap
    cmap = get_cmap('viridis')
    cores_anos = {ano: cmap(i/len(anos)) for i, ano in enumerate(anos)}

    # Gráfico facetado por região
    st.subheader(f"Média Mensal de {nome_var} por Região (2020-2025)")
    fig, axes = plt.subplots(nrows=1, ncols=len(regioes), figsize=(5*len(regioes), 5), sharey=True)
    if len(regioes) == 1:
        axes = [axes]  # Garante iterabilidade se só uma região

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        for ano in anos:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty:
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        ax.set_title(regiao)
        ax.set_xlabel('Mês')
        if i == 0:
            ax.set_ylabel(nome_var)
        ax.set_xticks(meses)
        ax.grid(True)

    # Adicionar legenda fora dos subplots
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.05, 1))

    plt.tight_layout(rect=[0, 0, 0.95, 1])
    st.pyplot(fig)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
