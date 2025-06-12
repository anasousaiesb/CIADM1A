import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap
import textwrap # Import for textwrap.dedent

# --- CONFIGURAÇÕES DA PÁGINA E ESTILO GLOBAL ---
st.set_page_config(
    layout="wide",
    page_title="Clima Brasil: Análise de Sazonalidade e Tendências 🇧🇷",
    initial_sidebar_state="expanded",
    page_icon="🌈" # Um ícone divertido para a aba do navegador
)

# Caminho relativo ao arquivo CSV (ajuste se necessário)
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

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
        # Se não há como calcular e a coluna não existe, o erro será tratado no bloco principal
        pass

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano', 'Regiao']) # Remove NAs de colunas essenciais
    
    # Renomear colunas para exibição amigável no selectbox
    df.rename(columns={
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'Precipitação Total (mm)',
        'RADIACAO GLOBAL (Kj/m²)': 'Radiação Global (Kj/m²)'
    }, inplace=True)

    return df

# --- TÍTULO PRINCIPAL E INTRODUÇÃO ---
st.title("☀️ Clima Brasil: Uma Viagem Visual por Sazonalidade e Tendências! 🌦️")
st.markdown(textwrap.dedent("""
<style>
    /* Estilos para a fonte grande e média na introdução */
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
        color: #4CAF50; /* Um verde mais vibrante */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .medium-font {
        font-size: 16px !important;
        color: #007BFF; /* Um azul mais claro e vibrante */
    }
    /* Estilos para os selectboxes e botões */
    .stSelectbox label {
        font-weight: bold;
        color: #34495E; /* Azul escuro quase preto */
        font-size: 1.1em;
    }
    .stButton>button {
        background-color: #FF6F61; /* Coral vibrante */
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px; /* Mais arredondado */
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #FF5A4D; /* Um pouco mais escuro ao passar o mouse */
    }
    /* Estilos para os subheaders (subtítulos) */
    h2 {
        color: #2E86C1; /* Azul celeste */
        font-size: 28px;
        border-bottom: 3px solid #2E86C1; /* Borda mais grossa */
        padding-bottom: 8px;
        margin-top: 40px;
        margin-bottom: 20px;
        text-shadow: 0.5px 0.5px 1px rgba(0,0,0,0.1);
    }
    /* Estilos para as caixas de informação */
    .info-box {
        background-color: #e3f2fd; /* Azul claro */
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #2196f3; /* Azul primário */
        margin-top: 15px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.15);
    }
    .warning-box {
        background-color: #fff3e0; /* Laranja claro */
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #ff9800; /* Laranja primário */
        margin-top: 15px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.15);
    }
    .error-box {
        background-color: #ffebee; /* Vermelho claro */
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #f44336; /* Vermelho primário */
        margin-top: 15px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.15);
    }
    .success-box {
        background-color: #e8f5e9; /* Verde claro */
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #4CAF50; /* Verde primário */
        margin-top: 15px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.15);
    }
</style>
<p class="big-font">✨ Prepare-se para uma imersão nos padrões climáticos do Brasil! ✨</p>
<p class="medium-font">Navegue pelas **variações sazonais** e desvende as **tendências anuais** das variáveis climáticas mais importantes em cada região. Uma ferramenta interativa para insights e formulação de hipóteses sobre o nosso clima tropical.</p>
"""), unsafe_allow_html=True)

st.markdown("---") # Linha divisória para separar visualmente as seções

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia
    if 'Temp_Media' not in df_unificado.columns:
        error_message_temp_media = textwrap.dedent("""
        <div class="error-box">
            ❌ <b>Erro Crítico:</b> A coluna 'Temp_Media' não existe e não pôde ser calculada a partir das colunas de máxima e mínima.<br>
            Por favor, verifique se seu arquivo CSV contém as colunas <code>'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'</code> e <code>'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'</code> ou uma coluna <code>'Temp_Media'</code> já calculada.
        </div>
        """)
        st.error(error_message_temp_media, unsafe_allow_html=True)
        st.stop()

    # --- INTERFACE DO USUÁRIO (BARRA LATERAL) ---
    st.sidebar.header("⚙️ **Filtros e Configurações**")
    
    # Garantir que as regiões sejam únicas e ordenadas
    regioes = sorted(df_unificado['Regiao'].dropna().unique())
    todos_anos_disponiveis = sorted(df_unificado['Ano'].dropna().unique())
    # meses_disponiveis não usado diretamente no selectbox, mas pode ser útil para debug/expansões
    # meses_disponiveis = sorted(df_unificado['Mês'].dropna().unique())

    # Seleção de Região
    regiao_selecionada = st.sidebar.selectbox(
        "1. 📍 **Escolha sua Região:**",
        regioes,
        index=regioes.index("Sul") if "Sul" in regioes else 0 # Define "Sul" como padrão se disponível
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
        error_message_vars_missing = textwrap.dedent("""
        <div class="error-box">
            ❌ <b>Erro:</b> Nenhuma das variáveis climáticas esperadas (Temperatura Média, Precipitação Total, Radiação Global) foi encontrada no seu arquivo CSV.
            Verifique os nomes das colunas!
        </div>
        """)
        st.error(error_message_vars_missing, unsafe_allow_html=True)
        st.stop()

    nome_var = st.sidebar.selectbox(
        "2. 🌡️ **Qual Variável Climática Analisar?**",
        list(variaveis_disponiveis.keys()),
        index=list(variaveis_disponiveis.keys()).index('Temperatura Média (°C)') if 'Temperatura Média (°C)' in variaveis_disponiveis else 0 # Padrão Temperatura
    )
    coluna_var = variaveis_disponiveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # --- VISUALIZAÇÃO PRINCIPAL (Sazonalidade Anual) ---
    st.subheader(f"📈 Sazonalidade Anual de **{nome_var}** na Região **{regiao_selecionada}**")
    st.markdown("Acompanhe as flutuações mensais para cada ano e compare-as com a média histórica regional. Observe os ciclos e as variações ano a ano! 🧐")

    # Filtrar dados para a região selecionada
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada].copy()

    # Cores para os anos (Esquema de cores 'inferno' é vibrante e acessível)
    cmap = get_cmap('inferno') 
    # Garante que as cores sejam distribuídas uniformemente entre os anos disponíveis
    cores_anos = {ano: cmap(i / (len(todos_anos_disponiveis) - 1) if len(todos_anos_disponiveis) > 1 else 1)
                  for i, ano in enumerate(todos_anos_disponiveis)}

    # Criando o gráfico de sazonalidade
    fig, ax = plt.subplots(figsize=(15, 8)) # Tamanho maior para mais impacto

    valores_anuais_por_mes = {}
    for ano in todos_anos_disponiveis:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty and df_ano_regiao.dropna().any():
            ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', markersize=6, linestyle='-', 
                    color=cores_anos.get(ano, 'lightgray'), label=f'{int(ano)}', linewidth=2, alpha=0.8)
            valores_anuais_por_mes[ano] = df_ano_regiao.values

    # Calcula e plota a média histórica
    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    ax.plot(media_historica_mensal.index, media_historica_mensal.values, 
            linestyle='--', color='black', label=f'Média Histórica ({int(min(todos_anos_disponiveis))}-{int(max(todos_anos_disponiveis))})', linewidth=3, alpha=0.9)

    # Configurações do gráfico
    ax.set_title(f'Variação Mensal de {nome_var} por Ano em {regiao_selecionada}', fontsize=20, color='#34495E', fontweight='bold')
    ax.set_xlabel('Mês', fontsize=15, color='#555555')
    ax.set_ylabel(f'{nome_var} ({unidade_var})', fontsize=15, color='#555555')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], fontsize=12)
    ax.tick_params(axis='x', rotation=45) # Rotaciona labels para evitar sobreposição
    ax.grid(True, linestyle=':', alpha=0.7, color='lightgray')
    ax.legend(title='Anos do Período', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize=11, title_fontsize='13', frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")

    # --- NOVA SEÇÃO: FORMULAÇÃO DE HIPÓTESES ---
    st.header("🧠 Que hipóteses sobre o clima futuro podemos formular? 🤔")
    warning_message_short_term = textwrap.dedent("""
    <div class="warning-box">
        🚨 <b>Importante:</b> Esta análise baseia-se em dados de <b>curto prazo (2020-2025)</b>. As 'tendências' e 'hipóteses' são exercícios exploratórios e <b>NÃO são previsões climáticas definitivas</b>. Previsões rigorosas exigem séries históricas de dados de décadas e modelos climáticos complexos e validados.
    </div>
    """)
    st.warning(warning_message_short_term, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # --- HIPÓTESE 1: ANÁLISE DE TENDÊNCIA ANUAL ---
        st.subheader("1. 📈 Hipótese de Tendência Anual")
        st.markdown("Analisamos a média anual da variável para identificar se há um padrão de aumento, diminuição ou estabilidade ao longo do tempo. 👀")

        # Calcula a média anual da variável para a região
        media_anual = df_regiao.groupby('Ano')[coluna_var].mean().dropna()
        
        if len(media_anual) > 1:
            anos_validos = media_anual.index.astype(int)
            valores_validos = media_anual.values

            # Calcula a linha de tendência usando regressão linear
            slope, intercept = np.polyfit(anos_validos, valores_validos, 1)
            trend_line = slope * anos_validos + intercept
            
            # Gráfico de Tendência
            fig_trend, ax_trend = plt.subplots(figsize=(8, 5)) # Ajuste para caber na coluna e ser mais visível
            ax_trend.plot(anos_validos, valores_validos, marker='o', markersize=7, linestyle='-', color='#007BFF', label='Média Anual Observada') # Azul vibrante
            ax_trend.plot(anos_validos, trend_line, linestyle='--', color='#DC3545', label='Linha de Tendência', linewidth=2.5) # Vermelho intenso
            ax_trend.set_title(f'Tendência Anual de {nome_var} em {regiao_selecionada}', fontsize=16, color='#34495E')
            ax_trend.set_xlabel('Ano', fontsize=12, color='#555555')
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})', fontsize=12, color='#555555')
            ax_trend.grid(True, linestyle=':', alpha=0.6, color='lightgray')
            ax_trend.legend(fontsize=10)
            plt.tight_layout()
            st.pyplot(fig_trend)

            # Interpretação da tendência
            if abs(slope) > 0.05: # Limiar para considerar uma tendência significativa
                tendencia_direcao = "aumento" if slope > 0 else "diminuição"
                emoji_tendencia = "🔥" if slope > 0 and nome_var == 'Temperatura Média (°C)' else "❄️" if slope < 0 and nome_var == 'Temperatura Média (°C)' else ""
                if nome_var == 'Precipitação Total (mm)':
                    emoji_tendencia = "🌧️" if slope > 0 else "☀️" # Para chuva/seca
                elif nome_var == 'Radiação Global (Kj/m²)':
                    emoji_tendencia = "☀️" if slope > 0 else "☁️" # Para radiação/nublado

                info_message_trend = textwrap.dedent(f"""
                <div class="info-box">
                    {emoji_tendencia} <b>Tendência de {tendencia_direcao.capitalize()}:</b> Observamos uma tendência de <b>{tendencia_direcao}</b> na {nome_var.lower()} para a região {regiao_selecionada}. A uma taxa de <code>{slope:.3f} {unidade_var}/ano</code>, a hipótese é que a região pode enfrentar <b>condições progressivamente {tendencia_direcao.replace('aumento', 'mais intensas').replace('diminuição', 'mais amenas')}</b> se essa tendência de curto prazo continuar.
                </div>
                """)
                st.markdown(info_message_trend, unsafe_allow_html=True)
            else:
                success_message_stability = textwrap.dedent(f"""
                <div class="success-box">
                    ⚖️ <b>Tendência de Estabilidade:</b> A linha de tendência é quase plana (<code>{slope:.3f} {unidade_var}/ano</code>), sugerindo <b>relativa estabilidade</b> na média anual de {nome_var.lower()} na região {regiao_selecionada} durante este período. A hipótese principal seria a manutenção das condições médias atuais, mas com atenção à variabilidade entre os anos.
                </div>
                """)
                st.markdown(success_message_stability, unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes (menos de 2 anos com valores válidos) para calcular uma tendência anual para esta variável e região. 📊")

    with col2:
        # --- HIPÓTESE 2: ANÁLISE DE VARIABILIDADE E EXTREMOS ---
        st.subheader("2. 🌪️ Hipótese de Variabilidade Interanual")
        st.markdown("Compreenda quão 'estáveis' ou 'voláteis' foram os anos em relação à média histórica mensal. Anos com grandes desvios podem indicar eventos climáticos extremos. 💥")
        
        # Calcula o desvio absoluto médio de cada ano em relação à média histórica mensal
        if not df_valores_anuais.empty and not media_historica_mensal.empty:
            desvios_abs_anuais = (df_valores_anuais.subtract(media_historica_mensal, axis=0)).abs().mean()
            desvios_abs_anuais = desvios_abs_anuais.dropna()

            if not desvios_abs_anuais.empty:
                ano_mais_atipico = desvios_abs_anuais.idxmax()
                maior_desvio = desvios_abs_anuais.max()
                
                error_message_atypical_year = textwrap.dedent(f"""
                <div class="error-box">
                    🔥 Na Região <b>{regiao_selecionada}</b>, para a variável <b>{nome_var}</b>, o ano de <b>{int(ano_mais_atipico)}</b> se destaca como o <b>mais atípico</b> (ou extremo), com as médias mensais se afastando em média <b>{maior_desvio:.2f} {unidade_var}</b> da média histórica do período. Isso pode sugerir maior instabilidade climática neste ano.
                </div>
                """)
                st.markdown(error_message_atypical_year, unsafe_allow_html=True)
                
                hypothesis_variability_text = textwrap.dedent("""
                <b>Hipótese de Variabilidade:</b> Se os anos mais recentes (ex: 2024, 2025) aparecem consistentemente com os maiores desvios, isso pode sugerir que <b>o clima na região está se tornando mais variável e propenso a extremos</b>. Anos que se desviam significativamente da média (para cima ou para baixo) podem se tornar mais frequentes, impactando planejamento e recursos. 🌍
                """)
                st.markdown(hypothesis_variability_text, unsafe_allow_html=True)

                st.write("📊 **Ranking de Anos por Desvio (Atipicidade):**")
                desvios_df = pd.DataFrame(desvios_abs_anuais.sort_values(ascending=False), columns=['Desvio Médio Absoluto'])
                st.dataframe(desvios_df.style.format("{:.2f}").set_properties(**{'background-color': '#f2f2f2', 'color': 'black'}), use_container_width=True)
            else:
                st.info("Não há dados de desvio significativos para realizar a análise de variabilidade anual. 📉")
        else:
            st.info("Dados insuficientes para calcular a variabilidade anual (médias mensais ou históricas vazias). 🧐")

    st.markdown("---")
    st.markdown("🌟 Desenvolvido com paixão e dados para uma jornada climática inesquecível! Por [Seu Nome/Equipe] 🚀")

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    file_not_found_error_message = textwrap.dedent(f"""
    <div class="error-box">
        ❌ <b>Erro Crítico:</b> O arquivo de dados <code>'{caminho_arquivo_unificado}'</code> não foi encontrado.<br>
        Por favor, verifique o caminho e a existência do arquivo na pasta <code>medias</code>.
        <br>💡 <b>Dica:</b> Certifique-se de que o arquivo <code>medias_mensais_geo_2020_2025.csv</code> está localizado corretamente na pasta <code>medias</code> dentro do seu projeto.
    </div>
    """)
    st.error(file_not_found_error_message, unsafe_allow_html=True)
except KeyError as e:
    key_error_message = textwrap.dedent(f"""
    <div class="error-box">
        ❌ <b>Erro de Coluna:</b> A coluna esperada <code>'{e}'</code> não foi encontrada no arquivo CSV.<br>
        Verifique se o nome da coluna está correto e se o arquivo está no formato esperado.
        <br>💡 <b>Dica:</b> O arquivo CSV deve conter colunas como 'Regiao', 'Ano', 'Mês', e 'Temp_Media' (ou 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' para cálculo), além de 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' e 'RADIACAO GLOBAL (Kj/m²)'.
    </div>
    """)
    st.error(key_error_message, unsafe_allow_html=True)
except Exception as e:
    generic_error_message = textwrap.dedent(f"""
    <div class="error-box">
        💥 <b>Ops! Ocorreu um erro inesperado:</b> {e}<br>
        🔄 <b>Sugestão:</b> Tente recarregar a página. Se o problema persistir, pode ser um erro nos dados ou no script. Por favor, entre em contato com o suporte técnico se necessário.
    </div>
    """)
    st.error(generic_error_message, unsafe_allow_html=True)
