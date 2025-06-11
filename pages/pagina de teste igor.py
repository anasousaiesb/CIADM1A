import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path
from scipy import stats

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Análise Climática", layout="wide")

# --- FUNÇÃO PARA CARREGAR DADOS ---
@st.cache_data  # Cache para melhor performance
def load_data():
    # Caminhos possíveis (tente todos antes de falhar)
    possible_paths = [
        Path("medias") / "medias_mensais_geo_2020_2025.csv",  # Caminho relativo local
        Path(__file__).parent / "medias" / "medias_mensais_geo_2020_2025.csv",  # Relativo ao script
        Path(__file__).parent.parent / "medias" / "medias_mensais_geo_2020_2025.csv"  # Um nível acima
    ]
    
    for path in possible_paths:
        if path.exists():
            df = pd.read_csv(path)
            
            # Verifica colunas necessárias
            required_cols = {'REGIAO', 'MÊS', 'ANO', 'TEMPERATURA MAXIMA (°C)', 'TEMPERATURA MINIMA (°C)'}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                st.error(f"Colunas faltando: {missing}")
                return None
            
            return df
    
    # Se nenhum caminho funcionou, permitir upload
    uploaded_file = st.file_uploader("Arquivo não encontrado. Faça upload do CSV:", type="csv")
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    
    return None

# --- INTERFACE DO USUÁRIO ---
st.title("📈 Análise de Amplitude Térmica")
st.markdown("""
Analise a variação da temperatura por região, mês e ano.
""")

# Carrega os dados
df = load_data()

if df is None:
    st.warning("Por favor, faça upload do arquivo de dados ou verifique o caminho.")
    st.stop()

# --- PROCESSAMENTO DOS DADOS ---
# Calcula amplitude térmica
df['Amplitude_Termica'] = df['TEMPERATURA MAXIMA (°C)'] - df['TEMPERATURA MINIMA (°C)']

# Widgets de seleção
regioes = sorted(df['REGIAO'].unique())
REGIAO_DESEJADA = st.sidebar.selectbox("Selecione a Região:", regioes, index=regioes.index('Sudeste') if 'Sudeste' in regioes else 0)

# Filtra a região
df_regiao = df[df['REGIAO'] == REGIAO_DESEJADA].copy()

# --- VISUALIZAÇÕES ---
tab1, tab2, tab3 = st.tabs(["Distribuição Mensal", "Evolução Anual", "Heatmap"])

with tab1:
    st.subheader(f"Distribuição por Mês - {REGIAO_DESEJADA}")
    plt.figure(figsize=(12,6))
    sns.boxplot(x='MÊS', y='Amplitude_Termica', data=df_regiao, palette="coolwarm", showmeans=True)
    plt.title(f"Amplitude Térmica por Mês\nRegião: {REGIAO_DESEJADA}")
    plt.xlabel("Mês")
    plt.ylabel("Amplitude Térmica (°C)")
    st.pyplot(plt)

with tab2:
    st.subheader(f"Evolução Anual - {REGIAO_DESEJADA}")
    media_anual = df_regiao.groupby('ANO')['Amplitude_Termica'].mean()
    
    plt.figure(figsize=(12,6))
    sns.lineplot(x=media_anual.index, y=media_anual.values, marker='o', ci=95)
    plt.title(f"Média Anual da Amplitude Térmica\nRegião: {REGIAO_DESEJADA}")
    plt.xlabel("Ano")
    plt.ylabel("Amplitude Média (°C)")
    plt.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(plt)

with tab3:
    st.subheader(f"Variação Mensal-Anual - {REGIAO_DESEJADA}")
    pivot = df_regiao.pivot_table(values='Amplitude_Termica', index='ANO', columns='MÊS', aggfunc='median')
    
    plt.figure(figsize=(12,8))
    sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".1f", linewidths=.5)
    plt.title(f"Amplitude Térmica por Mês e Ano\nRegião: {REGIAO_DESEJADA}")
    st.pyplot(plt)

# --- ANÁLISE ESTATÍSTICA ---
st.sidebar.subheader("Análise Estatística")
if st.sidebar.button("Calcular Estatísticas"):
    with st.expander("📊 Resultados Estatísticos"):
        # Mês com maior amplitude
        mes_max = df_regiao.groupby('MÊS')['Amplitude_Termica'].median().idxmax()
        
        # Ano com maior amplitude
        ano_max = df_regiao.groupby('ANO')['Amplitude_Termica'].mean().idxmax()
        
        # Tendência temporal
        anos = df_regiao['ANO'].unique()
        if len(anos) >= 4:
            media_anual = df_regiao.groupby('ANO')['Amplitude_Termica'].mean()
            tau, p_value = stats.kendalltau(media_anual.index, media_anual.values)
        
        st.write(f"🔹 **Mês com maior amplitude:** {mes_max}")
        st.write(f"🔹 **Ano com maior amplitude:** {ano_max}")
        
        if len(anos) >= 4:
            st.write(f"🔹 **Tendência temporal (p-value):** {p_value:.4f}")
            st.write("✅ Tendência significativa" if p_value < 0.05 else "❌ Sem tendência significativa")

# --- DICAS PARA DEPLOY NO STREAMLIT CLOUD ---
st.sidebar.info("""
**Dicas para deploy:**
1. Certifique-se que o arquivo está na pasta `/medias`
2. Verifique o nome exato do arquivo
3. Confira os logs em caso de erro
""")
