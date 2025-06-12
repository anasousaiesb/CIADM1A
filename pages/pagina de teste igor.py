import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(
    page_title="Análise Climática Regional do Brasil",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌎 Análise Climática Regional do Brasil (2020-2025)")
st.markdown("Bem-vindo à ferramenta de análise climática. Explore as tendências de temperatura, precipitação e radiação solar em diferentes regiões do Brasil entre 2020 e 2025.")

# Caminho relativo ao arquivo CSV
# Ajuste conforme a estrutura do seu projeto.
# Recomenda-se criar uma pasta 'data' na raiz do projeto e colocar o CSV lá.
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """
    Carrega e processa o arquivo de dados climáticos.
    Tenta calcular 'Temp_Media' se não existir, e converte tipos.
    """
    try:
        df = pd.read_csv(caminho)
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{caminho}' não foi encontrado. Por favor, certifique-se de que o arquivo está no diretório correto.")
        st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        st.stop()

    # Calcula a Temp_Media se as colunas de max/min existirem e 'Temp_Media' não
    if 'Temp_Media' not in df.columns:
        if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
           'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
            df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
                                df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
        else:
            st.error("Erro: A coluna 'Temp_Media' não existe e não pôde ser calculada. Verifique o seu arquivo CSV.")
            st.stop()

    # Converte colunas essenciais para numérico, tratando erros
    for col in ['Mês', 'Ano']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            st.error(f"Erro: A coluna '{col}' não foi encontrada no arquivo CSV. Ela é essencial para a análise.")
            st.stop()

    df = df.dropna(subset=['Mês', 'Ano', 'Temp_Media']) # Garante que essas colunas não têm NaNs
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("⚙️ Selecione os Filtros")
    st.sidebar.markdown("Use os controles abaixo para personalizar sua visualização dos dados climáticos.")

    # Obter opções únicas para os filtros
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Dropdown para seleção de região
    regiao_selecionada = st.sidebar.selectbox(
        "📍 **Escolha a Região:**",
        regioes,
        help="Selecione uma das regiões brasileiras para analisar seus dados climáticos."
    )

    # Mapeamento de variáveis com nomes amigáveis e suas colunas reais
    variaveis = {
        'Temperatura Média (°C)': 'Temp_Media',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }
    nome_var = st.sidebar.selectbox(
        "📊 **Selecione a Variável:**",
        list(variaveis.keys()),
        help="Escolha entre Temperatura Média, Precipitação Total ou Radiação Global para visualizar."
    )
    coluna_var = variaveis[nome_var]

    # Verifica se a coluna da variável selecionada existe no DataFrame
    if coluna_var not in df_unificado.columns:
        st.error(f"A coluna '{coluna_var}' para '{nome_var}' não foi encontrada no arquivo CSV. Por favor, verifique o nome da coluna no seu arquivo.")
        st.stop()

    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # --- VISUALIZAÇÃO PRINCIPAL (Sazonalidade Anual) ---
    st.markdown("---")
    st.header(f"📈 Sazonalidade Climática: {nome_var} na Região {regiao_selecionada}")
    st.markdown(f"Este gráfico compara a variação mensal de **{nome_var}** para cada ano disponível na região **{regiao_selecionada}**, destacando a média histórica.")

    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada].copy() # Usar .copy() para evitar SettingWithCopyWarning

    # Cores para os anos com um mapa de cores mais vibrante
    cmap = get_cmap('viridis') # 'viridis', 'plasma', 'cividis', 'magma' são boas opções
    cores_anos = {ano: cmap(i / (len(anos) - 1 if len(anos) > 1 else 1)) for i, ano in enumerate(anos)}

    fig_sazonal, ax_sazonal = plt.subplots(figsize=(14, 7))

    valores_anuais_por_mes = {}
    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty:
            ax_sazonal.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-',
                            color=cores_anos.get(ano, 'gray'), label=str(int(ano)), linewidth=1.5, alpha=0.8)
        valores_anuais_por_mes[ano] = df_ano_regiao.values

    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    ax_sazonal.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='black',
                    label=f'Média Histórica ({int(min(anos))}-{int(max(anos))})', linewidth=3, alpha=0.9)

    ax_sazonal.set_title(f'Variação Mensal de {nome_var} por Ano - Região {regiao_selecionada}', fontsize=18, pad=20)
    ax_sazonal.set_xlabel('Mês', fontsize=14, labelpad=15)
    ax_sazonal.set_ylabel(f'{nome_var}', fontsize=14, labelpad=15)
    ax_sazonal.set_xticks(range(1, 13))
    ax_sazonal.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    ax_sazonal.grid(True, linestyle='--', alpha=0.7)
    ax_sazonal.legend(title='Ano', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    plt.tight_layout()
    st.pyplot(fig_sazonal)

    st.markdown("---")

    # --- NOVA SEÇÃO: FORMULAÇÃO DE HIPÓTESES ---
    st.header("🤔 Formulando Hipóteses sobre o Clima Futuro")
    st.info("🚨 **Importante:** As análises a seguir são baseadas em dados de **curto prazo (2020-2025)**. As 'tendências' e 'hipóteses' são exercícios exploratórios e **não devem ser consideradas previsões climáticas definitivas**. Previsões confiáveis exigem séries históricas de dados de décadas e modelos climáticos complexos.")

    col1, col2 = st.columns(2)

    with col1:
        # --- HIPÓTESE 1: ANÁLISE DE TENDÊNCIA ---
        st.subheader("1. Análise de Tendência Anual")
        st.markdown("Investiga se há um padrão de **aumento, diminuição ou estabilidade** na média anual da variável selecionada ao longo dos anos.")

        # Calcula a média anual da variável para a região
        media_anual = df_valores_anuais.mean(axis=0).dropna()

        if len(media_anual) > 1:
            anos_validos = media_anual.index.astype(int)
            valores_validos = media_anual.values

            # Calcula a linha de tendência usando regressão linear
            slope, intercept = np.polyfit(anos_validos, valores_validos, 1)
            trend_line = slope * anos_validos + intercept

            # Gráfico de Tendência
            fig_trend, ax_trend = plt.subplots(figsize=(7, 5))
            ax_trend.plot(anos_validos, valores_validos, marker='o', linestyle='-', label='Média Anual Observada', color='steelblue', markersize=7)
            ax_trend.plot(anos_validos, trend_line, linestyle='--', color='red', label=f'Linha de Tendência (Declive: {slope:.3f})', linewidth=2)
            ax_trend.set_title(f'Tendência Anual de {nome_var} na Região {regiao_selecionada}', fontsize=14, pad=10)
            ax_trend.set_xlabel('Ano', fontsize=12)
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})', fontsize=12)
            ax_trend.grid(True, linestyle='--', alpha=0.6)
            ax_trend.legend()
            plt.tight_layout()
            st.pyplot(fig_trend)

            # Interpretação da tendência
            tendencia_texto = ""
            if slope > 0.05: # Limiar para considerar uma tendência de aumento significativa
                tendencia_texto = f"**Conclusão: Tendência de Aumento** 📈\n\nOs dados sugerem uma tendência de **aumento** para a **{nome_var.lower()}** na região {regiao_selecionada}. Com uma taxa de variação de `{slope:.3f} {unidade_var} por ano`, a hipótese exploratória é que a região pode estar enfrentando **condições progressivamente mais quentes, chuvosas ou com maior radiação** se essa tendência de curto prazo persistir."
                st.success(tendencia_texto)
            elif slope < -0.05: # Limiar para considerar uma tendência de queda significativa
                tendencia_texto = f"**Conclusão: Tendência de Diminuição** 📉\n\nOs dados sugerem uma tendência de **diminuição** para a **{nome_var.lower()}** na região {regiao_selecionada}. Com uma taxa de variação de `{slope:.3f} {unidade_var} por ano`, a hipótese exploratória é que a região pode estar se tornando **mais fria, seca ou com menos radiação** se essa tendência de curto prazo continuar."
                st.warning(tendencia_texto)
            else:
                tendencia_texto = f"**Conclusão: Tendência de Estabilidade Relativa** ↔️\n\nA linha de tendência é quase plana (`{slope:.3f} {unidade_var} por ano`), sugerindo uma **relativa estabilidade** na média anual de **{nome_var.lower()}** na região {regiao_selecionada} durante este período. A hipótese principal seria a manutenção das condições médias atuais, mas é crucial observar a variabilidade entre os anos."
                st.info(tendencia_texto)

        else:
            st.info("Dados insuficientes (menos de 2 anos) para calcular uma tendência linear.")

    with col2:
        # --- HIPÓTESE 2: ANÁLISE DE VARIABILIDADE E EXTREMOS ---
        st.subheader("2. Análise de Variabilidade Anual")
        st.markdown("Avalia o quão distante cada ano esteve da média histórica, indicando a **ocorrência de anos mais atípicos ou extremos**.")

        # Calcula o desvio absoluto médio de cada ano em relação à média histórica mensal
        desvios_abs_anuais = (df_valores_anuais.subtract(media_historica_mensal, axis=0)).abs().mean()
        desvios_abs_anuais = desvios_abs_anuais.dropna()

        if not desvios_abs_anuais.empty:
            ano_mais_atipico = desvios_abs_anuais.idxmax()
            maior_desvio = desvios_abs_anuais.max()

            st.markdown(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
            st.markdown(f"- O ano de **{int(ano_mais_atipico)}** se destaca como o **mais atípico** (ou extremo) neste período, com as médias mensais se afastando em média **{maior_desvio:.2f} {unidade_var}** da média histórica geral.")

            st.markdown(f"**Hipótese de Variabilidade:** Se os anos mais recentes (por exemplo, {int(max(anos))-1} ou {int(max(anos))}) aparecem consistentemente com os maiores desvios, isso pode sugerir uma hipótese de que **o clima na região está se tornando mais variável e propenso a extremos** (tanto para cima quanto para baixo da média). Anos que se desviam significativamente da média podem se tornar mais frequentes.")

            st.write("---")
            st.markdown("**Ranking de Anos por Desvio (Indicador de Atipicidade):**")
            desvios_df = pd.DataFrame(desvios_abs_anuais, columns=['Desvio Médio Absoluto'])
            st.dataframe(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).style.format("{:.2f}"))
        else:
            st.info("Não há dados suficientes para realizar a análise de variabilidade anual.")

    st.markdown("---")
    st.markdown("""
        **Agradecemos por utilizar nossa ferramenta de análise climática!**
        Desenvolvido com ❤️ e dados abertos.
    """)

# --- TRATAMENTO GERAL DE ERROS ---
except Exception as e:
    st.error(f"Ocorreu um erro inesperado. Por favor, tente novamente ou contate o suporte. Detalhes: {e}")
