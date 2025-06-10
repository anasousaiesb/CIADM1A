import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Descobrindo o Clima do Brasil (2020-2025): Uma Jornada Interativa pelas Regiões e Variáveis Climáticas")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Calcular a Temperatura Média se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temperatura Média (°C)'] = (
            df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    elif 'Temperatura Média (°C)' not in df.columns:
        pass # Se não há como calcular e a coluna não existe, o erro será tratado no bloco principal

    # Certificar-se de que as colunas 'Mês' e 'Ano' são numéricas
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano'])
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia
    if 'Temperatura Média (°C)' not in df_unificado.columns:
        st.error("Erro Crítico: A coluna 'Temperatura Média (°C)' não existe e não pôde ser calculada a partir das colunas de máxima e mínima. Verifique o seu arquivo CSV.")
        st.stop()

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Explore Seus Dados Climáticos:")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    todos_anos_disponiveis = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Seleção interativa da variável, com 'Radiação Global (Kj/m²)' como padrão
    variaveis = {
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }
    if 'Radiação Global (Kj/m²)' in variaveis:
        default_var_index = list(variaveis.keys()).index('Radiação Global (Kj/m²)')
    else:
        default_var_index = 0

    nome_var = st.sidebar.selectbox("1. Qual Variável Climática Você Quer Analisar?", list(variaveis.keys()), index=default_var_index)
    coluna_var = variaveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # Seleção interativa de anos para o gráfico facetado
    anos_selecionados = st.sidebar.multiselect(
        "2. Selecione os Anos para o Gráfico Mensal:",
        options=todos_anos_disponiveis,
        default=todos_anos_disponiveis # Exibe todos por padrão
    )

    if not anos_selecionados:
        st.warning("Por favor, selecione pelo menos um ano para visualizar os dados. Use o filtro na barra lateral.")
        st.stop()

    # --- VISUALIZAÇÃO PRINCIPAL (Gráfico Facetado Interativo) ---
    st.subheader(f"Padrões Mensais de {nome_var} por Região (Anos Selecionados)")
    st.markdown("""
    Este painel interativo oferece uma visão abrangente dos padrões climáticos mensais para cada região do Brasil, no período de 2020 a 2025.
    Use os filtros na barra lateral para selecionar a variável climática de interesse e os anos que deseja comparar.
    Observe as variações sazonais, as diferenças entre as regiões e as flutuações anuais. **Quais regiões se destacam? Quais padrões se repetem?**
    """)
    
    n_cols = 3 # Número de colunas para os subplots
    n_rows = int(np.ceil(len(regioes) / n_cols))
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(5*n_cols, 4*n_rows), sharey=True)
    
    # Flatten axes if it's a 2D array, or ensure it's iterable if only one subplot
    if n_rows * n_cols > 1:
        axes = axes.flatten()
    elif len(regioes) == 1:
        axes = [axes]

    # Cores para os anos (garantindo que as cores sejam consistentes para todos os anos disponíveis)
    cmap = get_cmap('tab20') # 'tab20' oferece mais cores distintas
    cores_anos = {ano: cmap(i % cmap.N) for i, ano in enumerate(todos_anos_disponiveis)}

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        
        # Plotar apenas os anos selecionados pelo usuário
        for ano in anos_selecionados:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty:
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', 
                        color=cores_anos.get(ano, 'gray'), label=str(int(ano)), linewidth=1.5)
        
        # Plotar a média histórica de TODOS os anos disponíveis para contexto (opcional, pode ser removido se o foco for só nos anos selecionados)
        # media_historica_regiao = df_regiao.groupby('Mês')[coluna_var].mean().reindex(meses)
        # ax.plot(meses, media_historica_regiao.values, linestyle='--', color='black', label='Média Histórica', linewidth=2.5, alpha=0.7)

        ax.set_title(regiao, fontsize=14, fontweight='bold')
        ax.set_xlabel('Mês', fontsize=10)
        
        # Adicionar ylabel apenas na primeira coluna de cada linha para evitar poluição
        if i % n_cols == 0:
            ax.set_ylabel(f'{nome_var} {unidade_var}', fontsize=10)
        
        ax.set_xticks(meses)
        ax.set_xticklabels([f'{m:02d}' for m in meses]) # Formato de mês com 2 dígitos
        ax.grid(True, linestyle=':', alpha=0.7)

    # Remover subplots vazios, se houver
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Criar uma única legenda para todo o gráfico
    handles, labels = [], []
    # Pega handles e labels do primeiro subplot que tenha linhas plotadas
    for ax_item in axes:
        if ax_item and ax_item.lines:
            handles, labels = ax_item.get_legend_handles_labels()
            if handles: # Se encontrou handles, pode parar
                break
    
    if handles and labels:
        # Se você tiver a média histórica plotada em todos os subplots, pode querer adicioná-la aqui explicitamente
        # Ex: handles.append(Line2D([], [], color='black', linestyle='--', linewidth=2.5))
        # labels.append('Média Histórica')
        fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.05, 1), fontsize=10, title_fontsize='11')

    plt.tight_layout(rect=[0, 0, 0.95, 1]) # Ajusta para acomodar a legenda
    st.pyplot(fig)

    # --- Análise e Insights ---
    st.markdown("---")
    st.header("Seus Insights Climáticos: O Que os Dados Revelam?")
    st.markdown("""
    Este painel não é apenas um conjunto de gráficos; é uma janela para o comportamento climático dinâmico das regiões brasileiras.
    Use os filtros na barra lateral para moldar sua narrativa e descobrir padrões que podem ser cruciais para diversos setores.

    ### Guiando Sua Análise:
    * **Padrões Sazonais:** Observe como a linha de cada ano (e de cada variável) sobe e desce ao longo dos meses. Isso reflete as estações do ano e suas características climáticas. Por exemplo, chuvas de verão no Sudeste, ou o "inverno" amazônico.
    * **Diferenças Regionais:** Compare os gráficos entre as diferentes regiões. Qual região tem a temperatura mais estável? Qual tem a maior amplitude de precipitação? Essas diferenças são moldadas pela geografia e sistemas climáticos atuantes em cada área.
    * **Variabilidade Interanual:** Ao selecionar diferentes anos, note como um mesmo mês pode ter valores muito distintos entre um ano e outro. Isso é a **variabilidade climática**, e anos com desvios significativos podem indicar a ocorrência de eventos climáticos como:
        * **Ondas de Calor/Frio:** Picos ou vales extremos de temperatura.
        * **Secas/Inundações:** Meses com precipitação drasticamente abaixo ou acima da média.
        * **Anomalias de Radiação:** Dias/meses com sol atípico (muito ou pouco), afetando a energia solar.

    **Sua Tarefa:** Ao explorar, pergunte-se: "*Há algum ano que se destaca claramente em uma região?*", "*As tendências de uma variável se correlacionam com as de outra?*", "*O que esses padrões significam para a agricultura, recursos hídricos ou planejamento urbano daquela região?*"

    Permita que os dados contem a história, e use sua análise para destacar as conclusões mais impactantes!
    """)

    # --- Análise de Extremos de Radiação (mantido para contexto) ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.subheader("Foco Especial: Extremos de Radiação Global (2020-2025)")
        st.markdown("""
        Quando selecionamos a **Radiação Global**, é particularmente interessante identificar os momentos de maior e menor incidência solar.
        Esses pontos extremos são vitais para o planejamento de energia solar, agricultura e compreensão de eventos de seca ou excesso de nebulosidade.
        """)

        # Garante que a coluna de radiação existe e não está vazia
        if coluna_var in df_unificado.columns and not df_unificado[coluna_var].empty:
            # Identifica o maior valor de radiação global
            idx_max = df_unificado[coluna_var].idxmax()
            max_rad_data = df_unificado.loc[idx_max]

            # Identifica o menor valor de radiação global
            idx_min = df_unificado[coluna_var].idxmin()
            min_rad_data = df_unificado.loc[idx_min]

            st.markdown(f"""
            ### O Raio de Sol Mais Intenso ☀️

            O maior valor de Radiação Global registrado no período foi de **{max_rad_data[coluna_var]:.2f} Kj/m²**.
            * **Região:** {max_rad_data['Regiao']}
            * **Mês:** {max_rad_data['Mês']}
            * **Ano:** {max_rad_data['Ano']}
            """)

            st.markdown(f"""
            ### Os Dias de Menos Luz ☁️

            O menor valor de Radiação Global registrado no período foi de **{min_rad_data[coluna_var]:.2f} Kj/m²**.
            * **Região:** {min_rad_data['Regiao']}
            * **Mês:** {min_rad_data['Mês']}
            * **Ano:** {min_rad_data['Ano']}
            """)

            st.markdown("""
            ### Por Que Isso Importa? A Relevância dos Extremos

            A compreensão desses extremos de radiação é fundamental:

            * **Energia Solar:** Os picos indicam as melhores condições para a geração de energia fotovoltaica, enquanto os vales mostram desafios para sistemas solares.
            * **Agricultura e Biomas:** A radiação afeta diretamente a fotossíntese e a evapotranspiração, impactando o crescimento das plantas e o balanço hídrico dos ecossistemas.
            * **Clima e Ambiente:** Extremos de radiação influenciam a temperatura do ar e do solo, a formação de nuvens e até mesmo a qualidade do ar em áreas urbanas.

            Essas informações são poderosas para o planejamento de infraestrutura, estratégias agrícolas e para a adaptação às mudanças climáticas regionais.
            """)
        else:
            st.write("Dados de Radiação Global não disponíveis ou insuficientes para análise de extremos.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao gerar os gráficos: {e}")
