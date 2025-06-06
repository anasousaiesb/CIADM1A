import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# --- TÍTULO ATUALIZADO ---
st.title("Comparação Climática: Precipitação nas Regiões Norte vs. Sul (2020-2025)")

@st.cache_data
def carregar_dados(caminho):
    """
    Carrega os dados do arquivo CSV, valida colunas e realiza o pré-processamento.
    """
    df = pd.read_csv(caminho)

    # Validação crucial para garantir que a coluna de precipitação existe
    coluna_precipitacao = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'
    if coluna_precipitacao not in df.columns:
        raise KeyError(f"A coluna necessária '{coluna_precipitacao}' não foi encontrada no arquivo CSV.")

    # Garante que as colunas essenciais são numéricas
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')

    # Remove linhas onde os dados essenciais são nulos
    df = df.dropna(subset=['Mês', 'Ano', 'Regiao', coluna_precipitacao])
    return df

try:
    # Caminho do arquivo
    caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- FILTROS NA BARRA LATERAL ---
    st.sidebar.header("Filtros")
    anos_disponiveis = sorted(df_unificado['Ano'].unique().astype(int))
    anos_selecionados = st.sidebar.multiselect("Selecione os Anos para Análise:", options=anos_disponiveis, default=anos_disponiveis)

    if not anos_selecionados:
        st.warning("Por favor, selecione pelo menos um ano para continuar.")
        st.stop()

    # --- PREPARAÇÃO DOS DADOS FOCADA NA COMPARAÇÃO ---
    regioes_para_comparar = ['Norte', 'Sul']
    coluna_var = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'

    df_filtrado = df_unificado[df_unificado['Regiao'].isin(regioes_para_comparar) & df_unificado['Ano'].isin(anos_selecionados)]

    if df_filtrado.empty:
        st.error("Não foram encontrados dados de precipitação para as Regiões Norte/Sul nos anos selecionados.")
        st.stop()

    # --- VISUALIZAÇÃO GRÁFICA ---
    st.header("Comparação da Precipitação: Norte vs. Sul")

    fig, ax = plt.subplots(figsize=(12, 7))
    cores_regiao = {'Norte': '#0077b6', 'Sul': '#d9534f'}
    dados_volume = {}

    for regiao in regioes_para_comparar:
        df_regiao_filtrada = df_filtrado[df_filtrado['Regiao'] == regiao]
        if not df_regiao_filtrada.empty:
            media_mensal_regiao = df_regiao_filtrada.groupby('Mês')[coluna_var].mean().reindex(range(1, 13))

            volume_anual = media_mensal_regiao.sum()
            dados_volume[regiao] = f"{volume_anual:,.0f} mm/ano".replace(",", ".")

            ax.plot(media_mensal_regiao.index, media_mensal_regiao.values, marker='o', linestyle='-', color=cores_regiao[regiao], label=f'Região {regiao}', linewidth=2.5)

    ax.set_title("Comparação da Média Mensal de Precipitação (2020-2025)", fontsize=16)
    ax.set_xlabel("Mês", fontsize=12)
    ax.set_ylabel("Precipitação Média Mensal (mm)", fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)

    st.pyplot(fig)

    # --- ANÁLISE COMPARATIVA ---
    st.header("Justificativa das Diferenças Climáticas")

    st.markdown(f"""
    - 📍 **Região Norte:** Volume médio anual de **{dados_volume.get('Norte', 'N/D')}** mm.
        - Chuvas concentradas no **primeiro semestre**, intensificadas pela **Zona de Convergência Intertropical (ZCIT)**.
        - Evapotranspiração da floresta Amazônica impulsiona altos índices de precipitação.
        - **Estiagem no segundo semestre**, com redução significativa, mas sem seca absoluta.

    - 📍 **Região Sul:** Volume médio anual de **{dados_volume.get('Sul', 'N/D')}** mm.
        - Distribuição de chuvas **mais uniforme** ao longo do ano, sem estação seca definida.
        - Influência direta de **frentes frias**, gerando chuvas frequentes.
        - Fenômenos como **El Niño** e **La Niña** alteram padrões, causando períodos de excesso ou estiagem.

    🔎 **Resumo**: Enquanto o Norte tem chuvas intensas concentradas no início do ano devido à influência da ZCIT e da Amazônia, o Sul experimenta um padrão mais estável ao longo do ano, regulado por frentes frias e variações climáticas globais.
    """)

except KeyError as e:
    st.error(f"Erro na estrutura do arquivo CSV: {e}. Verifique se o nome da coluna está correto.")
except FileNotFoundError:
    st.error(f"Erro de Arquivo: '{caminho_arquivo_unificado}' não foi encontrado.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
