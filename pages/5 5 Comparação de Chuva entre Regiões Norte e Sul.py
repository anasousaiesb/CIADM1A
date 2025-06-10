import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Comparativo de Regimes de Precipitação: Regiões Norte e Sul do Brasil (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano'])

    # Garante que a coluna de precipitação existe
    if 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' not in df.columns:
        st.error("Erro Crítico: A coluna 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' não foi encontrada no arquivo CSV.")
        st.stop()
    return df

# --- CARREGAMENTO DOS DATADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # Filtrar apenas para as regiões Norte e Sul
    df_comparacao = df_unificado[df_unificado['Regiao'].isin(['Norte', 'Sul'])].copy()

    if df_comparacao.empty:
        st.error("Não há dados para as regiões 'Norte' ou 'Sul' no arquivo carregado.")
        st.stop()

    # Variável fixa para precipitação
    coluna_var = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'
    nome_var = 'Precipitação Total (mm)'
    unidade_var = '(mm)'

    # --- CONTROLE INTERATIVO: SELEÇÃO DE ANOS ---
    st.sidebar.header("Filtros de Visualização")
    todos_anos_disponiveis = sorted(df_comparacao['Ano'].unique())
    anos_selecionados = st.sidebar.multiselect(
        "Selecione os Anos para Comparar:",
        options=todos_anos_disponiveis,
        default=todos_anos_disponiveis # Seleciona todos por padrão
    )

    if not anos_selecionados:
        st.warning("Por favor, selecione pelo menos um ano para visualizar os dados.")
        st.stop()

    st.subheader(f"Comparativo Mensal de {nome_var} por Ano entre Regiões")

    regioes_comp = ['Norte', 'Sul']
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 7), sharey=True)
    fig.suptitle(f'Variação Mensal de {nome_var} por Ano - Regiões Norte e Sul', fontsize=18)

    cmap = get_cmap('viridis')

    for i, regiao in enumerate(regioes_comp):
        ax = axes[i]
        df_regiao = df_comparacao[df_comparacao['Regiao'] == regiao]
        
        valores_anuais_por_mes = {}
        # Apenas itera sobre os anos selecionados
        for ano in anos_selecionados:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
            if not df_ano_regiao.empty:
                cores_anos = {ano_val: cmap(j / (len(todos_anos_disponiveis) -1 if len(todos_anos_disponiveis) > 1 else 1)) for j, ano_val in enumerate(todos_anos_disponiveis)}
                ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos.get(ano, 'gray'), label=str(int(ano)))
            valores_anuais_por_mes[ano] = df_ano_regiao.values

        # A média histórica ainda considera todos os anos disponíveis para uma base de comparação consistente
        df_valores_anuais_para_media = pd.DataFrame({ano: df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13)).values for ano in todos_anos_disponiveis}, index=range(1, 13))
        media_historica_mensal = df_valores_anuais_para_media.mean(axis=1)


        ax.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='red', label=f'Média Histórica ({int(min(todos_anos_disponiveis))}-{int(max(todos_anos_disponiveis))})', linewidth=2.5)

        ax.set_title(f'Região {regiao}', fontsize=14)
        ax.set_xlabel('Mês', fontsize=12)
        ax.set_ylabel(nome_var, fontsize=12)
        ax.set_xticks(range(1, 13))
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    st.pyplot(fig)

    st.markdown("---")

    # --- Análise de volumes anuais (mantém o gráfico para todos os anos para contexto) ---
    st.subheader("Volumes Anuais de Precipitação")

    prec_anual_norte = df_comparacao[df_comparacao['Regiao'] == 'Norte'].groupby('Ano')[coluna_var].sum()
    prec_anual_sul = df_comparacao[df_comparacao['Regiao'] == 'Sul'].groupby('Ano')[coluna_var].sum()

    df_prec_anual = pd.DataFrame({
        'Norte': prec_anual_norte,
        'Sul': prec_anual_sul
    }).fillna(0)

    st.dataframe(df_prec_anual.style.format("{:.2f}"))

    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    df_prec_anual.plot(kind='bar', ax=ax_bar, colormap='Paired')
    ax_bar.set_title(f'Precipitação Anual Total por Região ({int(min(todos_anos_disponiveis))}-{int(max(todos_anos_disponiveis))})', fontsize=16)
    ax_bar.set_xlabel('Ano', fontsize=12)
    ax_bar.set_ylabel(f'Precipitação Total {unidade_var}', fontsize=12)
    ax_bar.tick_params(axis='x', rotation=45)
    ax_bar.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig_bar)

    st.markdown("---")

    # --- Justificativa das diferenças ---
    st.header("Justificativa das Diferenças nos Regimes de Precipitação")
    st.info("As justificativas a seguir são baseadas em conhecimentos geográficos e climáticos gerais do Brasil e complementam a análise dos dados. Elas ajudam a entender os padrões observados nos gráficos.")
    st.markdown("""
    As diferenças nos regimes de precipitação entre as Regiões Norte e Sul do Brasil são marcantes e refletem as distintas características geográficas e influências climáticas de cada área:

    ### Região Norte (Clima Equatorial)
    A Região Norte, dominada pela Floresta Amazônica, possui um clima predominantemente **Equatorial Úmido**.
    * **Volumes Elevados:** Caracteriza-se por altos volumes de precipitação ao longo do ano, frequentemente excedendo 2.000 mm anuais.
    * **Picos de Chuva:** Apresenta uma estação chuvosa bem definida, geralmente entre os meses de dezembro a maio (com picos entre março e abril), quando a Zona de Convergência Intertropical (ZCIT) atua com mais intensidade sobre a região.
    * **Secas Menos Pronunciadas:** Embora exista uma estação menos chuvosa (geralmente entre junho e novembro), ela não é uma "seca" no sentido tradicional, mas sim um período com menor volume de chuvas, que ainda são significativas. A evapotranspiração da própria floresta contribui para a manutenção da umidade e das chuvas.

    ### Região Sul (Clima Subtropical)
    A Região Sul, por sua vez, está localizada em latitudes médias e é influenciada por sistemas climáticos temperados e subtropicais, com a atuação frequente de massas de ar polares e frentes frias.
    * **Volumes Moderados a Altos:** Os volumes anuais de precipitação são significativos, mas geralmente menores que na Região Norte, variando em torno de 1.200 a 2.000 mm.
    * **Distribuição Mais Uniforme (com Sazonalidade):** Diferente do Norte, o Sul não possui uma estação seca tão nítida. As chuvas são mais bem distribuídas ao longo do ano, mas com tendências a picos.
        * **Picos de Chuva:** As chuvas de verão (dezembro a março) são influenciadas por sistemas convectivos, enquanto as chuvas de inverno (junho a agosto) estão ligadas à passagem de frentes frias e ciclones extratropicais. Isso pode resultar em dois picos, ou uma distribuição mais contínua dependendo da localidade.
        * **Eventos Extremos:** É mais propensa a eventos de chuva intensa e vendavais, especialmente durante a transição das estações.
    * **Secas Localizadas:** Embora menos comum que no Nordeste, por exemplo, períodos de estiagem podem ocorrer, especialmente se a atuação das frentes frias ou dos sistemas convectivos for irregular.

    ### Conclusão dos Regimes:
    Os gráficos provavelmente ilustram que a **Região Norte** mantém um padrão de elevada precipitação durante quase todo o ano, com um "inverno" amazônico (seco) menos rigoroso. Já a **Região Sul** exibe uma maior variabilidade sazonal, com chuvas bem distribuídas, mas com influências mais marcadas das estações, especialmente a passagem de frentes frias que podem trazer chuvas significativas no inverno, um contraste com a região Norte.
    """)

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
