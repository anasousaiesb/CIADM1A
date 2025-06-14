import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(
    layout="wide",
    page_title="Clima Brasil: Análise Interativa (2020-2025) 🇧🇷",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (NOVO: Mais abrangente para um visual moderno) ---
st.markdown("""
<style>
    /* Cores personalizadas */
    :root {
        --primary-color: #4CAF50; /* Verde vibrante */
        --secondary-color: #2196F3; /* Azul dinâmico */
        --text-color: #333333;
        --background-color: #f0f2f6; /* Cinza claro suave */
        --card-background: #ffffff;
        --border-color: #e0e0e0;
    }

    body {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: var(--text-color);
        background-color: var(--background-color);
    }

    .stApp {
        background-color: var(--background-color);
    }

    /* Títulos principais */
    h1 {
        color: #1a237e; /* Azul escuro profundo */
        text-align: center;
        font-size: 3.2em;
        margin-bottom: 0.5em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    h2 {
        color: var(--primary-color);
        font-size: 2.2em;
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.3em;
        margin-top: 1.5em;
        margin-bottom: 1em;
    }

    h3 {
        color: var(--secondary-color);
        font-size: 1.8em;
        margin-top: 1.2em;
        margin-bottom: 0.8em;
    }

    /* Estilo para a introdução */
    .big-font {
        font-size: 24px !important;
        font-weight: 600;
        color: #2e7d32; /* Verde escuro */
        text-align: center;
        margin-bottom: 15px;
    }
    .medium-font {
        font-size: 18px !important;
        color: #1976d2; /* Azul médio */
        text-align: center;
        margin-bottom: 25px;
    }

    /* Cartões de insights */
    .stMarkdown div[data-testid="stMarkdownContainer"] div {
        background-color: var(--card-background);
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        padding: 25px;
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    .stMarkdown div[data-testid="stMarkdownContainer"] div:hover {
        transform: translateY(-5px);
    }

    /* Melhorar legibilidade de listas */
    ul {
        margin-left: 20px;
        line-height: 1.7;
    }
    li {
        margin-bottom: 8px;
    }

    /* Botões e seletores na sidebar */
    .stSidebar .stSelectbox, .stSidebar .stMultiSelect {
        padding: 10px;
        border-radius: 8px;
        background-color: var(--card-background);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stSidebar label {
        font-weight: bold;
        color: #3f51b5; /* Índigo */
        font-size: 1.1em;
        margin-bottom: 10px;
    }

    /* Gráficos */
    .matplotlib {
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        overflow: hidden; /* Garante que a sombra não seja cortada */
    }

    /* Aviso e Erro */
    .stAlert {
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL E INTRODUÇÃO ---
st.title("🌎 Descobrindo o Clima do Brasil (2020-2025): Uma Jornada Interativa 📊")
st.markdown("""
<p class="big-font">Explore os padrões climáticos regionais e identifique tendências e anomalias nas temperaturas, precipitações e radiação solar.</p>
<p class="medium-font">Utilize os filtros na barra lateral para personalizar sua análise e mergulhar nos dados climáticos mais recentes do Brasil.</p>
""", unsafe_allow_html=True)

st.markdown("---") # Separador visual

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
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
    df['Regiao'] = df['Regiao'].map(mapa_regioes)
    
    # Calcular a Temperatura Média se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temperatura Média (°C)'] = (
            df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    elif 'Temperatura Média (°C)' not in df.columns:
        raise KeyError("Coluna 'Temperatura Média (°C)' não encontrada e não pôde ser calculada.")

    # Certificar-se de que as colunas 'Mês' e 'Ano' são numéricas
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano'])
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # --- INTERFACE DO USUÁRIO (BARRA LATERAL) ---
    st.sidebar.header("⚙️ Personalize sua Análise")
    
    regioes = sorted(df_unificado['Regiao'].dropna().unique())
    todos_anos_disponiveis = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Seleção interativa da variável climática
    variaveis = {
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }
    
    # Define a variável padrão e garante que ela exista no dicionário e nos dados
    default_var = 'Radiação Global (Kj/m²)'
    if default_var not in variaveis or variaveis[default_var] not in df_unificado.columns:
        default_var = 'Temperatura Média (°C)'
        if default_var not in variaveis or variaveis[default_var] not in df_unificado.columns:
            default_var = list(variaveis.keys())[0]

    default_var_index = list(variaveis.keys()).index(default_var)

    nome_var = st.sidebar.selectbox(
        "1. 🌡️ Qual Variável Climática Você Quer Analisar?",
        list(variaveis.keys()),
        index=default_var_index
    )
    coluna_var = variaveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # Seleção interativa de anos para o gráfico facetado
    st.sidebar.markdown("---")
    anos_selecionados = st.sidebar.multiselect(
        "2. 📅 Selecione os Anos para o Gráfico Mensal:",
        options=todos_anos_disponiveis,
        default=todos_anos_disponiveis # Exibe todos por padrão
    )

    if not anos_selecionados:
        st.warning("⚠️ **Atenção:** Por favor, selecione pelo menos um ano para visualizar os dados. Use o filtro na barra lateral.")
        st.stop()
    
    # --- VISUALIZAÇÃO PRINCIPAL (Gráfico Facetado Interativo) ---
    st.subheader(f"📈 Padrões Mensais de **{nome_var}** por Região")
    st.markdown(f"""
    Esta seção apresenta como a **{nome_var}** varia mês a mês em cada região do Brasil,
    para os anos selecionados: **{', '.join(map(str, sorted(anos_selecionados)))}**.
    Observe as tendências sazonais e as diferenças anuais para insights valiosos!
    """)
    
    n_cols = 3 # Número de colunas para os subplots
    n_rows = int(np.ceil(len(regioes) / n_cols))
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(5*n_cols, 4.5*n_rows), sharey=True, dpi=100)
    plt.style.use('seaborn-v0_8-darkgrid') # Estilo mais moderno e com grade

    if n_rows * n_cols > 1:
        axes = axes.flatten()
    elif len(regioes) == 1:
        axes = [axes]

    # Cores para os anos (usando 'tab20' para mais distinção)
    cmap = get_cmap('tab20')
    cores_anos = {ano: cmap(i % cmap.N) for i, ano in enumerate(todos_anos_disponiveis)}

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        
        for ano in anos_selecionados:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty and df_ano_regiao.dropna().any():
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', 
                        color=cores_anos.get(ano, 'gray'), label=str(int(ano)), linewidth=2.0)
        
        ax.set_title(f"📍 {regiao}", fontsize=15, fontweight='bold', color='#2F4F4F')
        ax.set_xlabel('Mês', fontsize=12)
        
        if i % n_cols == 0:
            ax.set_ylabel(f'{nome_var}\n({unidade_var})', fontsize=12)
            
        ax.set_xticks(meses)
        ax.set_xticklabels([f'{m:02d}' for m in meses], fontsize=10)
        ax.tick_params(axis='y', labelsize=10)
        ax.grid(True, linestyle=':', alpha=0.6)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    handles, labels = [], []
    for ax_item in fig.get_axes():
        if ax_item and ax_item.lines:
            for line in ax_item.lines:
                if line.get_label() not in labels and line.get_label() != '_nolegend_':
                    handles.append(line)
                    labels.append(line.get_label())
    
    if handles and labels:
        fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.08, 1), 
                   fontsize=11, title_fontsize='13', frameon=True, fancybox=True, shadow=True)

    plt.tight_layout(rect=[0, 0, 0.95, 1])
    st.pyplot(fig)

    # --- Análise e Insights ---
    st.markdown("---")
    st.header("💡 Seus Insights Climáticos: O Que os Dados Revelam?")
    st.markdown("""
    Este painel não é apenas um conjunto de gráficos; é uma **janela interativa** para o comportamento climático dinâmico das regiões brasileiras.
    Use os filtros na barra lateral para moldar sua narrativa e descobrir padrões que podem ser cruciais para diversos setores,
    como agricultura, gestão de recursos hídricos, planejamento urbano e muito mais!
    """)
    
    st.markdown("""
    ### 🎯 Guiando Sua Análise Profunda:
    * **Padrões Sazonais Clássicos:** Observe como a linha de cada ano (e de cada variável) sobe e desce ao longo dos meses. Isso reflete as estações do ano e suas características climáticas inerentes. Por exemplo, note os picos de chuva no verão do Sudeste ou o período mais seco no Centro-Oeste.
    * **Diferenças Regionais Marcantes:** Compare os gráficos entre as diferentes regiões. Qual região exibe a temperatura mais estável durante o ano? Qual delas possui a maior amplitude na precipitação? Essas distinções são fundamentalmente moldadas pela geografia única e pelos sistemas climáticos atuantes em cada área do Brasil.
    * **Variabilidade Interanual e Eventos Extremos:** Ao selecionar e comparar diferentes anos, preste atenção em como um mesmo mês pode apresentar valores muito distintos entre um ano e outro. Isso é a **variabilidade climática interanual**, e anos com desvios significativos podem indicar a ocorrência de fenômenos climáticos notáveis, como:
        * 🔥 **Ondas de Calor/Frio Incomuns:** Picos ou vales extremos de temperatura.
        * 💧 **Secas Severas/Inundações:** Meses com precipitação drasticamente abaixo ou muito acima da média histórica.
        * ☀️ **Anomalias de Radiação Solar:** Períodos com incidência solar atípica (excesso de sol resultando em mais calor e evaporação, ou excesso de nebulosidade).
    """)
    
    st.markdown("""
    **💭 Sua Tarefa:** Ao explorar os dados, faça-se perguntas instigantes:
    * "*Há algum ano que se destaca de forma inusitada em uma região específica para a variável que estou analisando?*"
    * "*As tendências observadas em uma variável (ex: temperatura) parecem se correlacionar com as de outra (ex: precipitação)?*"
    * "*O que esses padrões e desvios significam para a **sustentabilidade**, a **economia** e a **vida** nas regiões do Brasil?*"
    """)

    # --- Análise de Extremos de Radiação (com emojis e melhor formatação) ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.markdown("---")
        st.header("⚡ Foco Especial: Análise de Extremos de Radiação Global")
        st.markdown("""
        A radiação solar é uma variável climática de **extrema importância**. Ao focar nela, podemos identificar os momentos de maior e menor incidência solar,
        que são cruciais para setores como **energia fotovoltaica**, **agricultura** e para entender **eventos de seca** ou **excessiva nebulosidade**.
        """)

        if coluna_var in df_unificado.columns and not df_unificado[coluna_var].empty and df_unificado[coluna_var].max() > 0:
            # Identifica o maior valor de radiação global
            idx_max = df_unificado[coluna_var].idxmax()
            max_rad_data = df_unificado.loc[idx_max]

            # Identifica o menor valor de radiação global (apenas valores > 0 para evitar leituras de sensores off)
            min_valid_rad = df_unificado[df_unificado[coluna_var] > 0][coluna_var].min()
            idx_min_valid = df_unificado[df_unificado[coluna_var] == min_valid_rad].index[0]
            min_rad_data = df_unificado.loc[idx_min_valid]

            col_max, col_min = st.columns(2)

            with col_max:
                st.markdown(f"""
                <div style="background-color:#fffde7; padding: 20px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h4 style="color:#ffc107;">☀️ Raio de Sol Mais Intenso Registrado</h4>
                    <p style="font-size:1.1em;">O **maior valor** de Radiação Global foi de:</p>
                    <p style="font-size:1.8em; font-weight:bold; color:#f57c00;">{max_rad_data[coluna_var]:.2f} Kj/m²</p>
                    <ul>
                        <li><span style="font-weight:bold;">Região:</span> {max_rad_data['Regiao']}</li>
                        <li><span style="font-weight:bold;">Mês:</span> {int(max_rad_data['Mês']):02d}</li>
                        <li><span style="font-weight:bold;">Ano:</span> {int(max_rad_data['Ano'])}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col_min:
                st.markdown(f"""
                <div style="background-color:#e0f2f7; padding: 20px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h4 style="color:#0288d1;">☁️ Período de Menos Luz Solar (Excluindo Zeros)</h4>
                    <p style="font-size:1.1em;">O **menor valor significativo** de Radiação Global foi de:</p>
                    <p style="font-size:1.8em; font-weight:bold; color:#01579b;">{min_rad_data[coluna_var]:.2f} Kj/m²</p>
                    <ul>
                        <li><span style="font-weight:bold;">Região:</span> {min_rad_data['Regiao']}</li>
                        <li><span style="font-weight:bold;">Mês:</span> {int(min_rad_data['Mês']):02d}</li>
                        <li><span style="font-weight:bold;">Ano:</span> {int(min_rad_data['Ano'])}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            ### 🌟 Por Que Isso Importa? A Relevância dos Extremos de Radiação

            A compreensão desses extremos de radiação é **fundamental** para diversas aplicações:

            * **Energia Solar:** Os picos de radiação indicam as melhores condições para otimizar a geração de energia fotovoltaica, enquanto os vales apontam desafios que sistemas solares devem contornar.
            * **Agricultura e Biomas:** A radiação afeta diretamente a fotossíntese (crescimento das plantas) e a evapotranspiração, impactando diretamente a produtividade agrícola e o balanço hídrico natural dos ecossistemas.
            * **Clima e Ambiente:** Extremos de radiação influenciam a temperatura do ar e do solo, a formação de nuvens e podem até ter um impacto na qualidade do ar, especialmente em grandes centros urbanos.

            Essas informações são **poderosas ferramentas** para o planejamento de infraestrutura resiliente, o desenvolvimento de estratégias agrícolas inteligentes e para a adaptação estratégica às mudanças climáticas em nível regional.
            """)
        else:
            st.info("ℹ️ Dados de Radiação Global não disponíveis ou insuficientes para uma análise significativa de extremos para a variável selecionada.")

except FileNotFoundError:
    st.error(f"❌ **Erro Crítico:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo na pasta `medias`.")
    st.info("💡 **Dica:** Certifique-se de que o arquivo `medias_mensais_geo_2020_2025.csv` está localizado corretamente na pasta `medias` dentro do seu projeto.")
except KeyError as e:
    st.error(f"❌ **Erro de Dados:** A coluna esperada '{e}' não foi encontrada no arquivo CSV ou não pôde ser calculada. Verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média.")
    st.info("💡 **Dica:** O arquivo CSV deve conter colunas como 'Regiao', 'Ano', 'Mês', e, para temperatura média, 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' ou já ter uma coluna 'Temperatura Média (°C)'.")
except Exception as e:
    st.error(f"💥 **Ops! Ocorreu um erro inesperado:** {e}")
    st.warning("🔄 **Sugestão:** Tente recarregar a página. Se o problema persistir, pode ser um erro nos dados ou no script. Por favor, entre em contato com o suporte técnico se necessário.")

st.markdown("---")
st.markdown("Desenvolvido com 💙 e dados abertos para o conhecimento climático. [Ana Sophia e Igor Andrade] © 2025")
