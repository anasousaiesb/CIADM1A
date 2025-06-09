import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

st.title("Médias Mensais Regionais por Ano")

# Caminho relativo ao arquivo CSV dentro do projeto
# Adapte o caminho do arquivo conforme a sua organização!
# Exemplo: "medias/medias_mensais_geo_temp_media_2017.csv"
# Para múltiplos anos, o ideal é ter um arquivo único (ex: medias_mensais_geo_temp_media_completo.csv)
# ou arquivos separados por ano na mesma pasta.

# Opção 1: Arquivo único (recomendado)
caminho_arquivo = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

try:
    # Ler o arquivo CSV (deve conter coluna "Ano")
    df_medias_geo = pd.read_csv(caminho_arquivo)

    # Checa se há coluna Ano e filtra anos disponíveis
    if 'Ano' not in df_medias_geo.columns:
        st.error("O arquivo CSV deve conter uma coluna 'Ano'.")
        st.stop()
    anos_disponiveis = sorted(df_medias_geo['Ano'].unique())
    ano_selecionado = st.selectbox("Selecione o ano:", anos_disponiveis)

    # Filtra dados para o ano selecionado
    df_ano = df_medias_geo[df_medias_geo['Ano'] == ano_selecionado]

    # Lista de regiões e meses únicas
    regioes = df_ano['Regiao'].unique()
    meses = sorted(df_ano['Mês'].unique())

    # Seleção interativa da variável
    variaveis = [
        'RADIACAO GLOBAL (Kj/m²)',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'
    ]
    # Corrige nomes das colunas caso estejam em KJ ou Kj
    variaveis_corrigidas = []
    for v in variaveis:
        if v in df_ano.columns:
            variaveis_corrigidas.append(v)
        elif v.replace("Kj", "KJ") in df_ano.columns:
            variaveis_corrigidas.append(v.replace("Kj", "KJ"))
        else:
            variaveis_corrigidas.append(v)  # Mantém nome original se não encontrar
    variavel = st.selectbox("Selecione a variável para visualizar:", variaveis_corrigidas)

    # --- Gráficos por Região (Média Regional) ---
    st.subheader(f"Médias Mensais Regionais de {variavel} - {ano_selecionado}")
    fig, ax = plt.subplots(figsize=(12, 6))
    for regiao in regioes:
        # Filtra o DataFrame para a região atual
        df_regiao = df_ano[df_ano['Regiao'] == regiao]
        # Calcula a média da variável para cada mês dentro da região
        media_regional = df_regiao.groupby('Mês')[variavel].mean().reindex(meses)
        if variavel.startswith('TEMPERATURA'):
            ax.plot(media_regional.index, media_regional.values, marker='o', label=f'{regiao} - {variavel.split(" ")[0]}')
        else:
            ax.plot(media_regional.index, media_regional.values, marker='o', label=regiao)
    ax.set_title(f'Médias Mensais Regionais de {variavel} - {ano_selecionado}')
    ax.set_xlabel('Mês')
    ax.set_ylabel(variavel)
    ax.set_xticks(meses)
    ax.grid(True)
    ax.legend(title='Região')
    plt.tight_layout()
    st.pyplot(fig)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
