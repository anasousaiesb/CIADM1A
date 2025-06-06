import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Análise Climática Regional do Brasil (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS (CACHEADA) ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Pré-processamento: Calcula a Temp_Media se as colunas de max/min existirem
    # Isso não força o uso, apenas cria a coluna se for possível, para uso posterior.
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] + 
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano'])
    return df

# --- BLOCO PRINCIPAL DO SCRIPT ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- INTERFACE DO USUÁRIO NA BARRA LATERAL ---
    st.sidebar.header("Filtros de Visualização")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", regioes)

    variaveis = {
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Temperatura Média (°C)': 'Temp_Media',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }
    # A variável 'Precipitação' agora é a primeira da lista, tornando-se o padrão.
    nome_var = st.sidebar.selectbox("Selecione a Variável:", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]
    
    # --- VERIFICAÇÃO DINÂMICA DA COLUNA SELECIONADA (CORREÇÃO PRINCIPAL) ---
    # O script agora verifica se a coluna ESCOLHIDA PELO USUÁRIO existe.
    if coluna_var not in df_unificado.columns:
        st.error(f"Erro Crítico: A coluna '{coluna_var}' necessária para a variável '{nome_var}' não foi encontrada no arquivo CSV.")
        if nome_var == 'Temperatura Média (°C)':
            st.info("Lembre-se: Para a temperatura, o script busca a coluna 'Temp_Media' ou tenta calculá-la a partir das colunas de temperatura máxima e mínima.")
        st.stop() # Para a execução se a coluna específica não existe.


    # --- LÓGICA DE PROCESSAMENTO E PLOTAGEM ---
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]

    # --- VISUALIZAÇÃO PRINCIPAL (Sazonalidade Anual) ---
    st.subheader(f"Comparativo Anual de {nome_var} na Região {regiao_selecionada}")

    cmap = get_cmap('plasma')
    cores_anos = {ano: cmap(i / (len(anos) -1 if len(anos) > 1 else 1)) for i, ano in enumerate(anos)}

    fig, ax = plt.subplots(figsize=(12, 6))

    valores_anuais_por_mes = {}
    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty:
            ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos.get(ano, 'gray'), label=str(int(ano)))
        valores_anuais_por_mes[ano] = df_ano_regiao.values

    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    ax.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='black', label=f'Média Histórica ({int(min(anos))}-{int(max(anos))})', linewidth=2.5)

    ax.set_title(f'Variação Mensal de {nome_var} por Ano - {regiao_selecionada}', fontsize=16)
    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel(nome_var, fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")

    # --- SEÇÃO DE ANÁLISE E HIPÓTESES ---
    st.header("Que hipóteses sobre o clima futuro podem ser formuladas com base nestes dados?")
    st.warning("🚨 **Aviso:** A análise a seguir baseia-se em dados de curto prazo (2020-2025). As 'tendências' e 'hipóteses' são exercícios exploratórios e **não devem ser consideradas previsões climáticas definitivas**, que exigem séries de dados de décadas.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hipótese 1: Análise de Tendência Anual")
        media_anual = df_valores_anuais.mean(axis=0).dropna()
        
        if len(media_anual) > 1:
            anos_validos = media_anual.index.astype(int)
            valores_validos = media_anual.values
            slope, intercept = np.polyfit(anos_validos, valores_validos, 1)
            trend_line = slope * anos_validos + intercept
            
            fig_trend, ax_trend = plt.subplots(figsize=(6, 4))
            ax_trend.plot(anos_validos, valores_validos, marker='o', linestyle='-', label='Média Anual Observada')
            ax_trend.plot(anos_validos, trend_line, linestyle='--', color='red', label='Linha de Tendência')
            ax_trend.set_title(f'Tendência Anual de {nome_var}')
            ax_trend.set_xlabel('Ano')
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})')
            ax_trend.grid(True, linestyle='--', alpha=0.5)
            ax_trend.legend()
            st.pyplot(fig_trend)
            
            limiar = 0.1 # Limiar para considerar uma tendência significativa
            if nome_var == 'Temperatura Média (°C)': limiar = 0.05
            
            if slope > limiar:
                tendencia_texto = f"**Tendência de Aumento:** Os dados sugerem uma tendência de **aumento** para a {nome_var.lower()} na região {regiao_selecionada}. A uma taxa de `{slope:.3f} {unidade_var}/ano`, a hipótese é de que a região pode enfrentar **condições progressivamente mais quentes/chuvosas/irradiadas**."
            elif slope < -limiar:
                tendencia_texto = f"**Tendência de Diminuição:** Os dados sugerem uma tendência de **diminuição** para a {nome_var.lower()} na região {regiao_selecionada}. A uma taxa de `{slope:.3f} {unidade_var}/ano`, a hipótese é de que a região pode estar se tornando **mais fria/seca/com menos radiação**."
            else:
                tendencia_texto = f"**Tendência de Estabilidade:** A linha de tendência é quase plana (`{slope:.3f} {unidade_var}/ano`), sugerindo **relativa estabilidade** na média anual de {nome_var.lower()} durante este período."
            
            st.markdown(tendencia_texto)
        else:
            st.info("Dados insuficientes (menos de 2 anos) para calcular uma tendência.")

    with col2:
        st.subheader("Hipótese 2: Análise de Variabilidade")
        desvios_abs_anuais = (df_valores_anuais.subtract(media_historica_mensal, axis=0)).abs().mean().dropna()

        if not desvios_abs_anuais.empty:
            ano_mais_atipico = desvios_abs_anuais.idxmax()
            maior_desvio = desvios_abs_anuais.max()
            
            st.markdown(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
            st.markdown(f"- O ano de **{int(ano_mais_atipico)}** se destaca como o **mais atípico** (ou extremo), com as médias mensais se afastando em média **{maior_desvio:.2f} {unidade_var}** da média histórica do período.")
            
            st.markdown("**Hipótese de Variabilidade:** Se os anos mais recentes aparecem com os maiores desvios, isso pode sugerir que **o clima na região está se tornando mais variável e propenso a extremos**.")
            st.write("**Ranking de Anos por Desvio (Atipicidade):**")
            desvios_df = pd.DataFrame(desvios_abs_anuais, columns=['Desvio Médio Absoluto'])
            st.dataframe(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).style.format("{:.2f}"))
        else:
            st.info("Não há dados suficientes para realizar a análise de variabilidade anual.")

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
