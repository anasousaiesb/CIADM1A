import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Desvendando o Clima do Brasil (2020-2025): Uma Análise Regional Interativa")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Calcula a Temp_Media se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] + 
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    elif 'Temp_Media' not in df.columns:
        pass # O erro será tratado no bloco principal

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano'])
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia
    if 'Temp_Media' not in df_unificado.columns:
        st.error("Erro Crítico: A coluna 'Temp_Media' não existe e não pôde ser calculada a partir das colunas de máxima e mínima. Verifique o seu arquivo CSV.")
        st.stop()

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Explore os Dados Climáticos:")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    todos_anos_disponiveis = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Seleção de Região
    regiao_selecionada = st.sidebar.selectbox("Escolha a Região para Análise Detalhada:", regioes)

    # Seleção de Variável Climática
    variaveis = {
        'Temperatura Média (°C)': 'Temp_Media',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }
    nome_var = st.sidebar.selectbox("Qual Variável Climática Você Quer Analisar?", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # Seleção Interativa de Anos
    anos_para_plot = st.sidebar.multiselect(
        "Selecione os Anos para o Gráfico Mensal:",
        options=todos_anos_disponiveis,
        default=todos_anos_disponiveis # Exibe todos por padrão
    )

    if not anos_para_plot:
        st.warning("Por favor, selecione pelo menos um ano para visualizar os dados mensais.")
        st.stop()

    # --- VISUALIZAÇÃO PRINCIPAL (Sazonalidade Anual) ---
    st.subheader(f"Padrões Anuais de {nome_var} na Região {regiao_selecionada}")
    st.markdown(f"Neste gráfico, você pode observar como a **{nome_var.lower()}** varia mês a mês na **Região {regiao_selecionada}**, destacando as tendências anuais e a média histórica do período.")

    # Cores para os anos (ESQUEMA DE CORES MAIS VIBRANTE E DISTINTO)
    # Usaremos um colormap diferente que oferece mais contraste ou um conjunto fixo de cores
    if len(anos_para_plot) > 0:
        cmap = get_cmap('tab10') # 'tab10' é bom para poucas categorias, 'viridis' ou 'plasma' para mais
        cores_dinamicas = {ano: cmap(i % cmap.N) for i, ano in enumerate(anos_para_plot)} # Cores mais distintas para os anos selecionados
    else:
        cores_dinamicas = {} # Caso nenhum ano seja selecionado

    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plotar apenas os anos selecionados pelo usuário
    for ano in anos_para_plot:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty:
            ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', 
                    color=cores_dinamicas.get(ano, 'gray'), label=str(int(ano)), linewidth=1.5)

    # Média histórica (calculada sobre TODOS os anos para referência consistente)
    valores_anuais_para_media = {}
    for ano in todos_anos_disponiveis:
        valores_anuais_para_media[ano] = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13)).values
    
    df_valores_anuais_completo = pd.DataFrame(valores_anuais_para_media, index=range(1, 13))
    media_historica_mensal = df_valores_anuais_completo.mean(axis=1)

    ax.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='darkred', 
            label=f'Média Histórica ({int(min(todos_anos_disponiveis))}-{int(max(todos_anos_disponiveis))})', 
            linewidth=3, alpha=0.8) # Linha da média mais proeminente

    ax.set_title(f'Variação Mensal de {nome_var} por Ano - {regiao_selecionada}', fontsize=18, fontweight='bold')
    ax.set_xlabel('Mês', fontsize=14)
    ax.set_ylabel(nome_var, fontsize=14)
    ax.set_xticks(range(1, 13))
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, title_fontsize='11')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")

    # --- NOVA SEÇÃO: FORMULAÇÃO DE HIPÓTESES CONVINCENTES ---
    st.header("O que estes dados nos dizem sobre o futuro do clima?")
    st.markdown("Os próximos insights são cruciais para entender potenciais **tendências e riscos climáticos** na região selecionada. Lembre-se, esses são exercícios exploratórios baseados em um período recente, mas que já apontam para direções importantes.")
    st.warning("🚨 **Atenção:** As 'hipóteses' apresentadas baseiam-se em dados de curto prazo (2020-2025). Embora valiosas para insights imediatos, **não devem ser consideradas previsões climáticas definitivas**, que exigem séries históricas de dados muito mais longas para maior precisão.")

    col1, col2 = st.columns(2)

    with col1:
        # --- HIPÓTESE 1: ANÁLISE DE TENDÊNCIA ---
        st.subheader("Análise de Tendência Anual: Estamos Caminhando para Qual Cenário?")
        st.markdown("Ao examinar a evolução da **média anual** da variável selecionada, podemos identificar se a região está se tornando consistentemente mais quente, úmida, seca ou ensolarada ao longo do tempo.")

        # Calcula a média anual da variável para a região (usando todos os anos para a tendência)
        media_anual = df_valores_anuais_completo.mean(axis=0).dropna()
        
        if len(media_anual) > 1:
            anos_validos = media_anual.index.astype(int)
            valores_validos = media_anual.values

            # Calcula a linha de tendência usando regressão linear
            slope, intercept = np.polyfit(anos_validos, valores_validos, 1)
            trend_line = slope * anos_validos + intercept
            
            # Gráfico de Tendência
            fig_trend, ax_trend = plt.subplots(figsize=(6, 4))
            ax_trend.plot(anos_validos, valores_validos, marker='o', linestyle='-', label='Média Anual Observada', color='steelblue')
            ax_trend.plot(anos_validos, trend_line, linestyle='--', color='darkorange', label='Linha de Tendência', linewidth=2) # Cor de destaque
            ax_trend.set_title(f'Tendência Anual de {nome_var}', fontsize=14, fontweight='bold')
            ax_trend.set_xlabel('Ano', fontsize=12)
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})', fontsize=12)
            ax_trend.grid(True, linestyle=':', alpha=0.6)
            ax_trend.legend(fontsize=10)
            plt.tight_layout()
            st.pyplot(fig_trend)

            # Interpretação da tendência - Linguagem mais persuasiva
            tendencia_texto = ""
            if slope > 0.05: # Limiar para considerar uma tendência de aumento
                tendencia_texto = f"📈 **Tendência de Aumento Visível:** Nossos dados revelam uma clara tendência de **aumento** para a {nome_var.lower()} na **Região {regiao_selecionada}**. Com um ritmo de **`{slope:.3f} {unidade_var}/ano`**, a hipótese é que a região pode estar entrando em um período de **condições progressivamente mais quentes, chuvosas ou com maior incidência solar**, o que exige atenção para planejamento e adaptação."
            elif slope < -0.05: # Limiar para considerar uma tendência de queda
                tendencia_texto = f"📉 **Tendência de Diminuição Observada:** Há uma indicação de **diminuição** na {nome_var.lower()} para a **Região {regiao_selecionada}**. Com uma taxa de `{slope:.3f} {unidade_var}/ano`, podemos hipotetizar que a região pode estar se direcionando para **condições mais frias, secas ou com menor radiação**, com implicações para setores como agricultura e recursos hídricos."
            else:
                tendencia_texto = f"↔️ **Estabilidade Notável:** A linha de tendência mostra uma **relativa estabilidade** (`{slope:.3f} {unidade_var}/ano`) na média anual de {nome_var.lower()} na **Região {regiao_selecionada}**. Isso sugere a manutenção das condições médias atuais, mas é crucial monitorar a variabilidade entre os anos, que pode ser o verdadeiro desafio."
            
            st.markdown(tendencia_texto)

        else:
            st.info("Dados insuficientes (menos de 2 anos) para calcular uma tendência significativa. Mais anos de dados seriam ideais para uma análise robusta.")

    with col2:
        # --- HIPÓTESE 2: ANÁLISE DE VARIABILIDADE E EXTREMOS ---
        st.subheader("Análise de Variabilidade: A Região Está Mais Sujeita a Extremos?")
        st.markdown("Entender a variabilidade de um ano para o outro é vital para prever a **frequência de eventos extremos**. Anos com maiores desvios da média histórica podem sinalizar um clima mais volátil.")
        
        # Calcula o desvio absoluto médio de cada ano em relação à média histórica mensal
        desvios_abs_anuais = (df_valores_anuais_completo.subtract(media_historica_mensal, axis=0)).abs().mean()
        desvios_abs_anuais = desvios_abs_anuais.dropna()

        if not desvios_abs_anuais.empty:
            ano_mais_atipico = desvios_abs_anuais.idxmax()
            maior_desvio = desvios_abs_anuais.max()
            
            st.markdown(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
            st.markdown(f"- O ano de **{int(ano_mais_atipico)}** se destaca como o **mais atípico** (ou extremo) do período, com as médias mensais se afastando em média **{maior_desvio:.2f} {unidade_var}** da média histórica. Isso aponta para condições significativamente diferentes do padrão usual.")
            
            st.markdown("""
            **🌊 Hipótese de Clima Extremo:** Se os anos mais recentes (como 2024, 2025) continuam a apresentar os maiores desvios, isso sugere uma hipótese preocupante: **o clima na região pode estar se tornando mais instável e propenso a eventos extremos** (ondas de calor, secas prolongadas, chuvas torrenciais). A flutuação crescente exige estratégias de resiliência e planejamento adaptativo.
            """)

            st.write("**Ranking de Anos por Atipicidade (Desvio Médio Absoluto):**")
            desvios_df = pd.DataFrame(desvios_abs_anuais, columns=['Desvio Médio Absoluto'])
            st.dataframe(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).style.format("{:.2f}"))
        else:
            st.info("Não há dados suficientes para realizar a análise de variabilidade anual. Considere a necessidade de mais dados para detectar padrões de extremos.")

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
