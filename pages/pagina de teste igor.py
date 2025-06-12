import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(
    layout="wide",
    page_title="Clima Brasil: Análise de Sazonalidade e Tendências 🇧🇷",
    initial_sidebar_state="expanded"
)

# Definindo o caminho do arquivo de dados (ajuste conforme a localização real do seu arquivo)
# Certifique-se de que 'medias_mensais_geo_2020_2025.csv' está na pasta 'medias'
caminho_arquivo_unificado = os.path.join('medias', 'medias_mensais_geo_2020_2025.csv')

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data(show_spinner="Carregando e processando os dados climáticos... ⏳")
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Mapeamento de abreviações de regiões para nomes completos
    mapa_regioes = {
        "CO": "Centro-Oeste",
        "NE": "Nordeste",
        "N": "Norte",
        "S": "Sul",
        "SE": "Sudeste"
    }
    df['Regiao'] = df['Regiao'].apply(lambda x: mapa_regioes.get(x, x)) 
    
    # Calcula a Temp_Media se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] + 
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    elif 'Temp_Media' not in df.columns:
        raise KeyError("Coluna 'Temp_Media' não encontrada e não pôde ser calculada a partir das colunas de máxima e mínima. Verifique seu CSV.")

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano', 'Regiao']) # Remove NAs de colunas essenciais
    
    # Assegurar que os nomes das variáveis estejam corretos para o selectbox
    df.rename(columns={
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'Precipitação Total (mm)',
        'RADIACAO GLOBAL (Kj/m²)': 'Radiação Global (Kj/m²)'
    }, inplace=True)

    return df

# --- TÍTULO PRINCIPAL E INTRODUÇÃO ---
st.title("🌦️ Jornada Climática Regional do Brasil (2020-2025)")
st.markdown("""
<style>
    .big-font {
        font-size:18px !important;
        font-weight: bold;
        color: #2e8b57; /* SeaGreen */
    }
    .medium-font {
        font-size:15px !important;
        color: #4682b4; /* SteelBlue */
    }
    .stSelectbox label {
        font-weight: bold;
        color: #333333;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
    }
    .stMarkdown h2 {
        color: #0F4C75; /* Darker Blue */
        font-size: 24px;
        border-bottom: 2px solid #0F4C75;
        padding-bottom: 5px;
        margin-top: 30px;
    }
</style>
<p class="big-font">Explore e compreenda as **variações sazonais** e **tendências anuais** das principais variáveis climáticas nas regiões do Brasil.</p>
<p class="medium-font">Esta ferramenta interativa permite visualizar padrões, identificar anomalias e formular hipóteses sobre o clima futuro.</p>
""", unsafe_allow_html=True)

st.markdown("---")

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # --- INTERFACE DO USUÁRIO (BARRA LATERAL) ---
    st.sidebar.header("⚙️ Configurações da Análise")
    
    regioes = sorted(df_unificado['Regiao'].dropna().unique())
    todos_anos_disponiveis = sorted(df_unificado['Ano'].unique())
    meses_disponiveis = sorted(df_unificado['Mês'].unique())

    # Seleção de Região
    regiao_selecionada = st.sidebar.selectbox(
        "1. 📍 **Selecione a Região:**",
        regioes,
        index=regioes.index("Sul") if "Sul" in regioes else 0 # Define "Sul" como padrão
    )

    # Seleção de Variável Climática
    variaveis = {
        'Temperatura Média (°C)': 'Temp_Media',
        'Precipitação Total (mm)': 'Precipitação Total (mm)',
        'Radiação Global (Kj/m²)': 'Radiação Global (Kj/m²)'
    }
    
    # Filtra as variáveis para mostrar apenas as colunas que realmente existem no DataFrame
    variaveis_disponiveis = {k: v for k, v in variaveis.items() if v in df_unificado.columns}
    
    if not variaveis_disponiveis:
        st.error("❌ Erro: Nenhuma das variáveis climáticas esperadas foi encontrada no seu arquivo CSV.")
        st.stop()

    nome_var = st.sidebar.selectbox(
        "2. 🌡️ **Qual Variável Climática Analisar?**",
        list(variaveis_disponiveis.keys()),
        index=list(variaveis_disponiveis.keys()).index('Temperatura Média (°C)') if 'Temperatura Média (°C)' in variaveis_disponiveis else 0 # Padrão Temperatura
    )
    coluna_var = variaveis_disponiveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # --- VISUALIZAÇÃO PRINCIPAL (Sazonalidade Anual) ---
    st.subheader(f"📊 Comparativo Anual de **{nome_var}** na Região **{regiao_selecionada}**")
    st.markdown("Acompanhe as flutuações mensais para cada ano e compare-as com a média histórica da região.")

    # Filtrar dados para a região selecionada
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada].copy() # Usar .copy()

    # Cores para os anos (Esquema de cores 'viridis' ou 'plasma' são bons para tendências)
    cmap = get_cmap('viridis') # 'viridis' é mais suave e acessível
    # Garante que as cores sejam distribuídas uniformemente entre os anos disponíveis
    cores_anos = {ano: cmap(i / (len(todos_anos_disponiveis) - 1) if len(todos_anos_disponiveis) > 1 else 1)
                  for i, ano in enumerate(todos_anos_disponiveis)}

    # Criando o gráfico
    fig, ax = plt.subplots(figsize=(14, 7)) # Ajustei o tamanho para ficar mais agradável

    valores_anuais_por_mes = {}
    for ano in todos_anos_disponiveis: # Itera por TODOS os anos para a média histórica
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty and df_ano_regiao.dropna().any():
            ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', 
                    color=cores_anos.get(ano, 'gray'), label=str(int(ano)), linewidth=1.5, alpha=0.7)
            valores_anuais_por_mes[ano] = df_ano_regiao.values

    # Calcula e plota a média histórica
    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    ax.plot(media_historica_mensal.index, media_historica_mensal.values, 
            linestyle='--', color='black', label=f'Média Período ({int(min(todos_anos_disponiveis))}-{int(max(todos_anos_disponiveis))})', linewidth=2.5, alpha=0.8)

    # Configurações do gráfico
    ax.set_title(f'Variação Mensal de {nome_var} por Ano em {regiao_selecionada}', fontsize=18, color='#2F4F4F', fontweight='bold')
    ax.set_xlabel('Mês', fontsize=14)
    ax.set_ylabel(f'{nome_var} ({unidade_var})', fontsize=14)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend(title='Legenda (Ano)', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize=10, title_fontsize='12')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")

    # --- NOVA SEÇÃO: FORMULAÇÃO DE HIPÓTESES ---
    st.header("🧠 Que hipóteses sobre o clima futuro podemos formular?")
    st.warning("🚨 **Importante:** Esta análise baseia-se em dados de curto prazo (2020-2025). As 'tendências' e 'hipóteses' são exercícios exploratórios e **NÃO são previsões climáticas definitivas**. Previsões rigorosas exigem séries históricas de dados de décadas e modelos climáticos complexos.")

    col1, col2 = st.columns(2)

    with col1:
        # --- HIPÓTESE 1: ANÁLISE DE TENDÊNCIA ANUAL ---
        st.subheader("1. 📈 Hipótese de Tendência Anual")

        # Calcula a média anual da variável para a região
        media_anual = df_regiao.groupby('Ano')[coluna_var].mean().dropna()
        
        if len(media_anual) > 1:
            anos_validos = media_anual.index.astype(int)
            valores_validos = media_anual.values

            # Calcula a linha de tendência usando regressão linear
            slope, intercept = np.polyfit(anos_validos, valores_validos, 1)
            trend_line = slope * anos_validos + intercept
            
            # Gráfico de Tendência
            fig_trend, ax_trend = plt.subplots(figsize=(7, 4)) # Ajuste para caber na coluna
            ax_trend.plot(anos_validos, valores_validos, marker='o', linestyle='-', color='dodgerblue', label='Média Anual Observada')
            ax_trend.plot(anos_validos, trend_line, linestyle='--', color='red', label='Linha de Tendência', linewidth=2)
            ax_trend.set_title(f'Tendência Anual de {nome_var} em {regiao_selecionada}', fontsize=14)
            ax_trend.set_xlabel('Ano', fontsize=11)
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})', fontsize=11)
            ax_trend.grid(True, linestyle='--', alpha=0.5)
            ax_trend.legend(fontsize=9)
            plt.tight_layout()
            st.pyplot(fig_trend)

            # Interpretação da tendência
            if abs(slope) > 0.05: # Limiar para considerar uma tendência significativa
                tendencia_direcao = "aumento" if slope > 0 else "diminuição"
                emoji_tendencia = "🔥" if slope > 0 else "❄️" # Para temperatura/calor
                if nome_var == 'Precipitação Total (mm)':
                    emoji_tendencia = "🌧️" if slope > 0 else "☀️" # Para chuva/seca
                elif nome_var == 'Radiação Global (Kj/m²)':
                    emoji_tendencia = "☀️" if slope > 0 else "☁️" # Para radiação/nublado

                st.markdown(f"""
                <div style="background-color:#e6f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; margin-top: 10px;">
                    <p style="font-size:1.05em;">{emoji_tendencia} **Tendência de {tendencia_direcao.capitalize()}:** Observamos uma tendência de **{tendencia_direcao}** na {nome_var.lower()} para a região {regiao_selecionada}. A uma taxa de `{slope:.3f} {unidade_var}/ano`, a hipótese é que a região pode enfrentar **condições progressivamente {tendencia_direcao.replace('aumento', 'mais intensas').replace('diminuição', 'mais amenas')}** se essa tendência de curto prazo continuar.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color:#fffde7; padding: 15px; border-radius: 10px; border-left: 5px solid #ffeb3b; margin-top: 10px;">
                    <p style="font-size:1.05em;">⚖️ **Tendência de Estabilidade:** A linha de tendência é quase plana (`{slope:.3f} {unidade_var}/ano`), sugerindo **relativa estabilidade** na média anual de {nome_var.lower()} na região {regiao_selecionada} durante este período. A hipótese principal seria a manutenção das condições médias atuais, mas com atenção à variabilidade entre os anos.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes (menos de 2 anos com valores válidos) para calcular uma tendência anual para esta variável e região.")

    with col2:
        # --- HIPÓTESE 2: ANÁLISE DE VARIABILIDADE E EXTREMOS ---
        st.subheader("2. 🌪️ Hipótese de Variabilidade Interanual")
        
        # Calcula o desvio absoluto médio de cada ano em relação à média histórica mensal
        if not df_valores_anuais.empty and not media_historica_mensal.empty:
            desvios_abs_anuais = (df_valores_anuais.subtract(media_historica_mensal, axis=0)).abs().mean()
            desvios_abs_anuais = desvios_abs_anuais.dropna()

            if not desvios_abs_anuais.empty:
                ano_mais_atipico = desvios_abs_anuais.idxmax()
                maior_desvio = desvios_abs_anuais.max()
                
                st.markdown(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
                st.markdown(f"""
                <div style="background-color:#ffebee; padding: 15px; border-radius: 10px; border-left: 5px solid #f44336; margin-top: 10px;">
                    <p style="font-size:1.05em;">
                        🔥 O ano de **{int(ano_mais_atipico)}** se destaca como o **mais atípico** (ou extremo), com as médias mensais se afastando em média **{maior_desvio:.2f} {unidade_var}** da média histórica do período. Isso sugere maior instabilidade climática neste ano.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                **Hipótese de Variabilidade:** Se os anos mais recentes (ex: 2024, 2025) aparecem consistentemente com os maiores desvios, isso pode sugerir que **o clima na região está se tornando mais variável e propenso a extremos**. Anos que se desviam significativamente da média (para cima ou para baixo) podem se tornar mais frequentes, impactando planejamento e recursos.
                """)

                st.write("📊 **Ranking de Anos por Desvio (Atipicidade):**")
                desvios_df = pd.DataFrame(desvios_abs_anuais.sort_values(ascending=False), columns=['Desvio Médio Absoluto'])
                st.dataframe(desvios_df.style.format("{:.2f}"), use_container_width=True)
            else:
                st.info("Não há dados de desvio significativos para realizar a análise de variabilidade anual.")
        else:
            st.info("Dados insuficientes para calcular a variabilidade anual (médias mensais ou históricas vazias).")

    st.markdown("---")
    st.markdown("🌟 Desenvolvido com paixão e dados por [Seu Nome/Equipe] 🌟")

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"❌ **Erro Crítico:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e a existência do arquivo na pasta `medias`.")
    st.info("💡 **Dica:** Certifique-se de que o arquivo `medias_mensais_geo_2020_2025.csv` está localizado corretamente na pasta `medias` dentro do seu projeto.")
except KeyError as e:
    st.error(f"❌ **Erro de Dados:** A coluna esperada '{e}' não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto e se o arquivo está no formato esperado.")
    st.info("💡 **Dica:** O arquivo CSV deve conter colunas como 'Regiao', 'Ano', 'Mês', e 'Temp_Media' (ou 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' para cálculo), além de 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' e 'RADIACAO GLOBAL (Kj/m²)'.")
except Exception as e:
    st.error(f"💥 **Ops! Ocorreu um erro inesperado:** {e}")
    st.warning("🔄 **Sugestão:** Tente recarregar a página. Se o problema persistir, pode ser um erro nos dados ou no script. Por favor, entre em contato com o suporte técnico se necessário.")
