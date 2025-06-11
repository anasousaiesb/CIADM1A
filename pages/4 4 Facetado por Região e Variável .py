import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Médias Mensais Regionais (2020-2025) - Visualização por Região e Variável")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Lista de regiões e anos únicas
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Seleção interativa da região
    regiao_selecionada = st.selectbox("Selecione a região para visualizar:", regioes)

    # Variáveis a serem plotadas
    variaveis = {
        'Temperatura Média (°C)': 'Temp_Media',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }

    # Seleção interativa da variável
    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Filtra o DataFrame para a região selecionada
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]

    st.subheader(f"Média Mensal de {nome_var} na Região {regiao_selecionada} (2020-2025)")
    fig, ax = plt.subplots(figsize=(8, 5))
    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
        if not df_ano_regiao.empty:
            ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
    ax.set_title(f'Média Mensal de {nome_var} - {regiao_selecionada} (2020-2025)')
    ax.set_xlabel('Mês')
    ax.set_ylabel(nome_var)
    ax.set_xticks(meses)
    ax.grid(True)
    ax.legend(title='Ano')
    plt.tight_layout()
    st.pyplot(fig)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
