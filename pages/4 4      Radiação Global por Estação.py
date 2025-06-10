import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Análise de Umidade Relativa do Ar (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Converte colunas para numérico, tratando erros
    cols_to_numeric = ['Mês', 'Ano', 'UMIDADE RELATIVA DO AR, HORARIA (%)']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['Mês', 'Ano', 'UMIDADE RELATIVA DO AR, HORARIA (%)'])
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de umidade existe
    if 'UMIDADE RELATIVA DO AR, HORARIA (%)' not in df_unificado.columns:
        st.error("Erro Crítico: A coluna 'UMIDADE RELATIVA DO AR, HORARIA (%)' não foi encontrada no arquivo CSV. Verifique o seu arquivo.")
        st.stop()

    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("---")
    st.header("Explorando Períodos de Baixa Umidade Relativa")
    st.markdown("""
        Esta aplicação permite identificar e analisar os períodos de **umidade relativa do ar muito baixa**
        em diferentes regiões do Brasil entre 2020 e 2025. Entender esses períodos é crucial para a
        saúde humana, agricultura, prevenção de incêndios e planejamento de recursos hídricos.
        """)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Análise")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", regioes)

    # NOVO: Limiar de Umidade Baixa
    limiar_umidade = st.sidebar.slider(
        "Defina o Limiar para Baixa Umidade (%):",
        min_value=10, max_value=60, value=30, step=5,
        help="Valores abaixo deste limiar serão considerados 'muito baixos'."
    )
    
    st.markdown("---")

    # --- VISUALIZAÇÃO 1: SAZONALIDADE DA UMIDADE ANUAL POR MÊS ---
    st.subheader(f"1. Sazonalidade da Umidade Relativa na Região {regiao_selecionada}")
    st.markdown(f"""
        Este gráfico de linha mostra a variação média da **Umidade Relativa do Ar**
        ao longo dos meses para cada ano na região **{regiao_selecionada}**.
        A linha tracejada preta representa a média histórica mensal para o período completo (2020-2025).
        
        **Interpretação:** Observe como a umidade sobe e desce anualmente. Períodos de baixa umidade
        tendem a se repetir nos mesmos meses a cada ano, revelando a sazonalidade. Fique atento
        às linhas que caem significativamente abaixo da média histórica, indicando anos mais secos.
        """)

    cmap = get_cmap('viridis') # Um esquema de cores diferente para variedade
    cores_anos = {ano: cmap(i / (len(anos) -1 if len(anos) > 1 else 1)) for i, ano in enumerate(anos)}

    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]

    fig, ax = plt.subplots(figsize=(12, 6))

    valores_anuais_por_mes = {}
    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')['UMIDADE RELATIVA DO AR, HORARIA (%)'].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty:
            ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos.get(ano, 'gray'), label=str(int(ano)))
        valores_anuais_por_mes[ano] = df_ano_regiao.values

    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    ax.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='black', label=f'Média Histórica ({int(min(anos))}-{int(max(anos))})', linewidth=2.5)

    ax.set_title(f'Variação Mensal da Umidade Relativa por Ano - {regiao_selecionada}', fontsize=16)
    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Umidade Relativa do Ar (%)', fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")

    # --- VISUALIZAÇÃO 2: DIAS/MESES COM UMIDADE ABAIXO DO LIMIAR ---
    st.subheader(f"2. Frequência de Baixa Umidade (< {limiar_umidade}%) em {regiao_selecionada}")
    st.markdown(f"""
        Este gráfico de barras mostra o número de **meses** em cada ano onde a umidade média
        da região **{regiao_selecionada}** caiu abaixo do limiar de **{limiar_umidade}%**.
        
        **Interpretação:** Barras mais altas indicam anos com maior frequência de meses secos.
        Isso pode sinalizar um risco aumentado para a saúde (problemas respiratórios),
        agricultura (perda de safras) e risco de incêndios florestais. Anos que se destacam
        com muitas ocorrências merecem uma investigação mais aprofundada.
        """)

    # Filtrar dados para umidade abaixo do limiar na região selecionada
    df_umidade_baixa_regiao = df_regiao[df_regiao['UMIDADE RELATIVA DO AR, HORARIA (%)'] < limiar_umidade]
    contagem_meses_secos = df_umidade_baixa_regiao.groupby('Ano')['Mês'].nunique().reindex(anos, fill_value=0)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    bar_colors = ['salmon' if count > 0 else 'lightgray' for count in contagem_meses_secos]
    bars = ax2.bar(contagem_meses_secos.index.astype(int), contagem_meses_secos.values, color=bar_colors)

    ax2.set_title(f'Número de Meses com Umidade Média < {limiar_umidade}% por Ano - {regiao_selecionada}', fontsize=14)
    ax2.set_xlabel('Ano', fontsize=12)
    ax2.set_ylabel('Número de Meses', fontsize=12)
    ax2.set_xticks(contagem_meses_secos.index.astype(int))
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, height, f'{int(height)}',
                     ha='center', va='bottom', color='black', fontsize=10)

    plt.tight_layout()
    st.pyplot(fig2)

    st.markdown("---")

    # --- VISUALIZAÇÃO 3: COMPARAÇÃO REGIONAL DE UMIDADE MÍNIMA ANUAL ---
    st.subheader(f"3. Umidade Relativa Mínima Anual por Região (2020-2025)")
    st.markdown("""
        Este gráfico de barras apresenta o **valor mínimo de Umidade Relativa do Ar**
        registrado em cada região, considerando todo o período de 2020 a 2025.
        
        **Interpretação:** Regiões com barras mais baixas indicam que, em algum momento,
        experimentaram condições de ar extremamente seco. Isso ajuda a identificar
        quais partes do Brasil são mais propensas a atingir níveis críticos de umidade.
        """)

    df_umidade_min_regional = df_unificado.groupby('Regiao')['UMIDADE RELATIVA DO AR, HORARIA (%)'].min().sort_values(ascending=True)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    bar_colors_min = ['skyblue' if regiao != regiao_selecionada else 'darkorange' for regiao in df_umidade_min_regional.index]
    bars3 = ax3.bar(df_umidade_min_regional.index, df_umidade_min_regional.values, color=bar_colors_min)

    ax3.set_title('Umidade Relativa Mínima Registrada por Região (2020-2025)', fontsize=16)
    ax3.set_xlabel('Região', fontsize=12)
    ax3.set_ylabel('Umidade Relativa Mínima (%)', fontsize=12)
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(axis='y', linestyle='--', alpha=0.6)

    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, yval + 1,
                 f'{yval:.1f}%', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    st.pyplot(fig3)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
