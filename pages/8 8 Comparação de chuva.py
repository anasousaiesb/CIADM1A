import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Norte vs. Sul: Análise de Chuvas",
    page_icon="🌦️",
    layout="wide"
)

# --- TÍTULO PRINCIPAL ---
st.title("🌦️ Análise Comparativa de Precipitação: Regiões Norte vs. Sul (2020-2025)")
st.markdown("Uma análise dos regimes de chuva, mostrando as diferenças de volume, picos e períodos de seca entre as duas regiões.")

# --- FUNÇÃO OTIMIZADA PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_e_preparar_dados(caminho):
    """
    Carrega, filtra e prepara os dados de precipitação para as regiões Norte e Sul.
    """
    try:
        df = pd.read_csv(caminho)
        
        # Filtrar apenas para as colunas e regiões de interesse
        colunas_necessarias = ['Regiao', 'Ano', 'Mês', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']
        if not all(col in df.columns for col in colunas_necessarias):
            st.error("O arquivo CSV não contém todas as colunas necessárias. Verifique o arquivo.")
            st.stop()
            
        df_filtrado = df[df['Regiao'].isin(['Norte', 'Sul'])][colunas_necessarias]
        
        # Garantir que os tipos de dados estão corretos
        for col in ['Ano', 'Mês', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')
        
        df_filtrado.dropna(inplace=True)
        return df_filtrado
        
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{caminho}' não foi encontrado. Verifique o caminho e o nome do arquivo.")
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        st.stop()

# --- CARREGAMENTO E PROCESSAMENTO ---
caminho_arquivo = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")
df_chuva = carregar_e_preparar_dados(caminho_arquivo)

# Calcular a média mensal de precipitação para cada região (agregando todos os anos)
media_norte = df_chuva[df_chuva['Regiao'] == 'Norte'].groupby('Mês')['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].mean()
media_sul = df_chuva[df_chuva['Regiao'] == 'Sul'].groupby('Mês')['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].mean()

# Garantir que todos os meses de 1 a 12 estão presentes
media_norte = media_norte.reindex(range(1, 13), fill_value=0)
media_sul = media_sul.reindex(range(1, 13), fill_value=0)

# --- GRÁFICO COMPARATIVO ---
st.header("Comparativo de Precipitação Mensal Média (2020-2025)")

fig, ax = plt.subplots(figsize=(12, 6))

# Plotar dados
ax.plot(media_norte.index, media_norte.values, marker='o', linestyle='-', color='#0077b6', label='Região Norte')
ax.plot(media_sul.index, media_sul.values, marker='x', linestyle='--', color='#d9534f', label='Região Sul')

# Estilização do Gráfico
ax.set_title('Média Mensal de Precipitação: Norte vs. Sul', fontsize=16, weight='bold')
ax.set_xlabel('Mês', fontsize=12)
ax.set_ylabel('Precipitação Média (mm)', fontsize=12)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(title='Região', fontsize=10)
plt.tight_layout()

st.pyplot(fig)


# --- ANÁLISE QUANTITATIVA E JUSTIFICATIVAS ---
st.markdown("---")
st.header("Análise Detalhada e Fatores Climáticos")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📊 Resumo dos Regimes de Chuva")
    
    # Calcular estatísticas
    stats = {
        'Região Norte': {
            'Volume Anual (mm)': media_norte.sum(),
            'Mês de Pico de Chuva': media_norte.idxmax(),
            'Pico (mm)': media_norte.max(),
            'Mês mais Seco': media_norte.idxmin(),
            'Seca (mm)': media_norte.min()
        },
        'Região Sul': {
            'Volume Anual (mm)': media_sul.sum(),
            'Mês de Pico de Chuva': media_sul.idxmax(),
            'Pico (mm)': media_sul.max(),
            'Mês mais Seco': media_sul.idxmin(),
            'Seca (mm)': media_sul.min()
        }
    }
    
    df_stats = pd.DataFrame(stats).T
    st.dataframe(df_stats.style.format({
        "Volume Anual (mm)": "{:.1f}",
        "Pico (mm)": "{:.1f}",
        "Seca (mm)": "{:.1f}",
        "Mês de Pico de Chuva": "{}",
        "Mês mais Seco": "{}"
    }).highlight_max(axis=0, color='#d4edda').highlight_min(axis=0, color='#f8d7da'))

with col2:
    st.subheader("🌍 Por que as Diferenças Ocorrem?")
    st.markdown("""
    As diferenças nos regimes de chuva entre o Norte e o Sul do Brasil são causadas por sistemas climáticos distintos que atuam em cada região.
    """)

with st.expander("**Clique aqui para ver a justificação climatológica detalhada**"):
    st.markdown("""
        ### 🌳 **Região Norte: O Domínio Equatorial**
        - **Causa Principal:** A principal fonte de chuva é a **Zona de Convergência Intertropical (ZCIT)**, uma faixa de nuvens e umidade que circunda o globo perto da linha do Equador.
        - **Pico de Chuva (Verão/Outono):** A ZCIT migra para o sul durante o verão do Hemisfério Sul (dezembro a março), causando chuvas intensas e volumosas na maior parte da Amazônia. Esse período é frequentemente chamado de "inverno amazônico".
        - **Período de Seca (Inverno/Primavera):** Quando a ZCIT se afasta para o norte, a região experimenta uma estação mais seca, especialmente entre junho e setembro.
        - **Evapotranspiração:** A própria Floresta Amazônica libera imensas quantidades de umidade na atmosfera (os "rios voadores"), o que alimenta ainda mais as chuvas locais.

        ### 🐧 **Região Sul: A Influência Polar**
        - **Causa Principal:** O regime de chuvas é dominado pela passagem de **sistemas frontais (frentes frias)**, que trazem massas de ar polar do sul.
        - **Distribuição Anual:** Ao contrário do Norte, a chuva no Sul é **melhor distribuída ao longo do ano**. Não há uma estação seca tão definida.
        - **Picos:** Embora chova o ano todo, os maiores volumes podem se concentrar na primavera e no verão devido ao encontro do ar quente e úmido com as frentes frias, gerando tempestades. O inverno também é úmido, mas com chuvas geralmente mais fracas e contínuas (chuviscos).
        - **Variabilidade:** A região pode sofrer tanto com secas (associadas a bloqueios atmosféricos) quanto com chuvas extremas, influenciadas por ciclones extratropicais.
    """)
