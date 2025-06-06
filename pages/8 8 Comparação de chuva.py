import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# --- TÍTULO FOI ALTERADO PARA REFLETIR O TEMA ---
st.title("Comparativo de Precipitação: Norte vs. Sul (2020-2025)")

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

    # Garante que as colunas importantes são numéricas
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

    # Filtro de Anos
    anos_disponiveis = sorted(df_unificado['Ano'].unique().astype(int))
    anos_selecionados = st.sidebar.multiselect(
        "Selecione os Anos para Análise:",
        options=anos_disponiveis,
        default=anos_disponiveis # Todos os anos selecionados por padrão
    )

    if not anos_selecionados:
        st.warning("Por favor, selecione pelo menos um ano para continuar.")
        st.stop()
        
    # --- PREPARAÇÃO DOS DADOS FOCADA NA COMPARAÇÃO ---
    regioes_para_comparar = ['Norte', 'Sul']
    coluna_var = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'
    
    df_filtrado = df_unificado[
        df_unificado['Regiao'].isin(regioes_para_comparar) &
        df_unificado['Ano'].isin(anos_selecionados)
    ]
    
    # --- AJUSTE: VERIFICAÇÃO SE EXISTEM DADOS PARA PLOTAR ---
    if df_filtrado.empty:
        st.error("Não foram encontrados dados de precipitação para a combinação de filtros selecionada (Regiões Norte/Sul e anos escolhidos).")
        st.info("Por favor, verifique se os anos selecionados contêm dados para as Regiões Norte e Sul no seu arquivo CSV.")
        st.stop()

    # --- GRÁFICO COMPARATIVO ÚNICO ---
    st.header("Variação Média Mensal da Precipitação")

    fig, ax = plt.subplots(figsize=(12, 7))
    
    cores_regiao = {'Norte': '#0077b6', 'Sul': '#d9534f'}
    dados_volume = {}

    for regiao in regioes_para_comparar:
        df_regiao_filtrada = df_filtrado[df_filtrado['Regiao'] == regiao]
        if not df_regiao_filtrada.empty:
            media_mensal_regiao = df_regiao_filtrada.groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
            
            volume_anual = media_mensal_regiao.sum()
            dados_volume[regiao] = f"{volume_anual:,.0f} mm/ano".replace(",",".")

            ax.plot(media_mensal_regiao.index, media_mensal_regiao.values, 
                    marker='o', linestyle='-', color=cores_regiao[regiao], label=f'Região {regiao}', linewidth=2.5)

    ax.set_title("Média Mensal de Precipitação (Norte vs. Sul)", fontsize=16)
    ax.set_xlabel("Mês", fontsize=12)
    ax.set_ylabel("Precipitação Média Mensal (mm)", fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)
    st.pyplot(fig)
    
    # --- ANÁLISE E JUSTIFICATIVA DAS DIFERENÇAS ---
    st.header("Análise e Justificativa Climática")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌦️ Região Norte")
        st.metric(label="Volume Médio Anual", value=dados_volume.get('Norte', 'N/D'))
        st.markdown("""
        - **Regime de Chuvas:** Caracterizado por **elevados volumes** e uma sazonalidade bem definida.
        - **Pico (Inverno Amazônico):** Ocorre tipicamente no **primeiro semestre** (pico entre Fev-Abr). Este período de chuvas intensas é causado pela forte atuação da **Zona de Convergência Intertropical (ZCIT)**.
        - **Período mais seco:** Ocorre no **segundo semestre**. Não é uma seca completa, mas uma redução significativa das chuvas, quando a ZCIT se desloca para o hemisfério norte.
        - **Fator Principal:** A **floresta amazônica** contribui com imensa umidade para a atmosfera (evapotranspiração), potencializando as chuvas.
        """)

    with col2:
        st.subheader("🌬️ Região Sul")
        st.metric(label="Volume Médio Anual", value=dados_volume.get('Sul', 'N/D'))
        st.markdown("""
        - **Regime de Chuvas:** É a região com a chuva **melhor distribuída ao longo do ano** no Brasil. Não há uma estação seca definida.
        - **Picos e Secas:** As chuvas são majoritariamente provocadas pela passagem de **sistemas frontais (frentes frias)**, que são frequentes durante todo o ano.
        - **Variabilidade:** O volume de chuva é muito influenciado por fenômenos como **El Niño** (que tende a aumentar as chuvas) e **La Niña** (que pode causar secas ou "estiagens" severas).
        - **Fator Principal:** A **localização em latitude média** (clima subtropical) a torna suscetível ao encontro de massas de ar frio e quente, gerando instabilidade e chuvas constantes.
        """)

except KeyError as e:
    st.error(f"Erro de Coluna: {e}. Verifique se o nome da coluna está correto no seu arquivo CSV.")
except FileNotFoundError:
    st.error(f"Erro de Arquivo: O arquivo no caminho '{caminho_arquivo_unificado}' não foi encontrado.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
