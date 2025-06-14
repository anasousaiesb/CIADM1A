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
    initial_sidebar_state="expanded",
    # Definindo um tema claro e cores principais
    # Isso pode ser feito via .streamlit/config.toml, mas para exemplo, faremos via CSS
)

# --- TÍTULO PRINCIPAL E INTRODUÇÃO ---
# Novo visual para o título principal com cor customizada
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');
    body {
        font-family: 'Poppins', sans-serif;
    }
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 3.2em; /* Bigger title */
        color: #2c3e50; /* Darker blue-grey for main title */
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .subtitle-text {
        font-size: 1.3em;
        font-weight: 600;
        color: #34495e; /* Slightly lighter blue-grey */
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .section-header {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 2em;
        color: #2980b9; /* A vibrant blue for section headers */
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 40px;
        margin-bottom: 25px;
    }
    .stSelectbox label, .stMultiSelect label, .stRadio label {
        font-weight: bold;
        color: #2c3e50;
    }
    .stMarkdown h3 {
        color: #2980b9;
        font-weight: 600;
        font-size: 1.6em;
    }
    .stMarkdown h4 {
        color: #e67e22; /* Orange for sub-sub headers */
        font-weight: 600;
        font-size: 1.3em;
    }
    .stMarkdown p {
        font-size: 1.05em;
        line-height: 1.6;
        color: #34495e;
    }
    .stMarkdown ul li {
        font-size: 1em;
        line-height: 1.5;
        color: #34495e;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<p class="main-title">🌎 Descobrindo o Clima do Brasil (2020-2025): Uma Jornada Interativa 📊</p>
<p class="subtitle-text">Explore os padrões climáticos regionais e identifique tendências e anomalias nas temperaturas, precipitações e radiação solar.</p>
<p class="subtitle-text">Utilize os filtros na barra lateral para personalizar sua análise e mergulhar nos dados.</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Caminho relativo ao arquivo CSV
# Certifique-se de que o arquivo 'medias_mensais_geo_2020_2025.csv' está na pasta 'medias'
# Ex: seu_projeto/medias/medias_mensais_geo_2020_2025.csv
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
        # Se não há como calcular e a coluna não existe, levanta um erro
        raise KeyError("Coluna 'Temperatura Média (°C)' não encontrada e não pôde ser calculada.")

    # Renomear colunas para facilitar o acesso e apresentação
    df = df.rename(columns={
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'Precipitação Total (mm)',
        'RADIACAO GLOBAL (Kj/m²)': 'Radiação Global (Kj/m²)'
    })

    # Certificar-se de que as colunas 'Mês' e 'Ano' são numéricas
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano']) # Remover linhas com Mês ou Ano inválidos
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # --- INTERFACE DO USUÁRIO (BARRA LATERAL) ---
    st.sidebar.header("⚙️ Personalize sua Análise")
    st.sidebar.markdown("Selecione as opções abaixo para filtrar os dados e visualizar diferentes aspectos do clima.")
    
    regioes = sorted(df_unificado['Regiao'].dropna().unique()) # Garante que regiões vazias não apareçam
    todos_anos_disponiveis = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Seleção interativa da variável climática
    variaveis = {
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'Precipitação Total (mm)',
        'Radiação Global (Kj/m²)': 'Radiação Global (Kj/m²)'
    }
    
    # Define a variável padrão e garante que ela exista no dicionário e nos dados
    default_var = 'Radiação Global (Kj/m²)'
    if default_var not in variaveis or variaveis[default_var] not in df_unificado.columns:
        default_var = 'Temperatura Média (°C)'
        if default_var not in variaveis or variaveis[default_var] not in df_unificado.columns:
            default_var = list(variaveis.keys())[0] # Fallback para a primeira variável disponível

    default_var_index = list(variaveis.keys()).index(default_var)

    nome_var = st.sidebar.selectbox(
        "1. 🌡️ Qual Variável Climática Você Quer Analisar?",
        list(variaveis.keys()),
        index=default_var_index,
        help="Escolha entre Temperatura Média, Precipitação Total ou Radiação Global para a análise."
    )
    coluna_var = variaveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # Seleção interativa de anos para o gráfico facetado
    st.sidebar.markdown("---")
    anos_selecionados = st.sidebar.multiselect(
        "2. 📅 Selecione os Anos para o Gráfico Mensal:",
        options=todos_anos_disponiveis,
        default=todos_anos_disponiveis, # Exibe todos por padrão
        help="Selecione um ou mais anos para comparar os padrões climáticos mensais."
    )

    if not anos_selecionados:
        st.warning("⚠️ **Atenção:** Por favor, selecione pelo menos um ano para visualizar os dados. Use o filtro na barra lateral.")
        st.stop()
        
    # --- VISUALIZAÇÃO PRINCIPAL (Gráfico Facetado Interativo) ---
    st.markdown(f"<h2 class='section-header'>📈 Padrões Mensais de **{nome_var}** por Região</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    Esta seção apresenta como a **{nome_var}** varia mês a mês em cada região do Brasil,
    para os anos **{', '.join(map(str, sorted(anos_selecionados)))}**.
    Observe as tendências sazonais e as diferenças anuais!
    """)
    
    n_cols = 3 # Número de colunas para os subplots
    n_rows = int(np.ceil(len(regioes) / n_cols))
    
    # Ajustando figsize para melhor visualização em telas wide
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(6*n_cols, 5*n_rows), sharey=True, dpi=100)
    plt.style.use('seaborn-v0_8-pastel') # Estilo mais suave e moderno

    # Flatten axes if it's a 2D array, or ensure it's iterable if only one subplot
    if n_rows * n_cols > 1:
        axes = axes.flatten()
    elif len(regioes) == 1:
        axes = [axes] # Garante que axes seja sempre uma lista para iteração

    # Cores para os anos (usando 'viridis' ou 'plasma' para um gradiente moderno)
    # 'tab20' é bom para distinção se houver muitos anos
    cmap_years = get_cmap('tab20')
    cores_anos = {ano: cmap_years(i % cmap_years.N) for i, ano in enumerate(todos_anos_disponiveis)}

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        
        # Plotar apenas os anos selecionados pelo usuário
        for ano in anos_selecionados:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty and df_ano_regiao.dropna().any(): # Verifica se há dados válidos para plotar
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', 
                        color=cores_anos.get(ano, 'gray'), label=str(int(ano)), linewidth=2.0, alpha=0.8)
        
        ax.set_title(f"📍 {regiao}", fontsize=16, fontweight='bold', color='#4a69bd') # Cor azul mais forte
        ax.set_xlabel('Mês', fontsize=13, color='#555')
        
        if i % n_cols == 0: # Adicionar ylabel apenas na primeira coluna de cada linha
            ax.set_ylabel(f'{nome_var}\n({unidade_var})', fontsize=13, color='#555')
            
        ax.set_xticks(meses)
        ax.set_xticklabels([f'{m:02d}' for m in meses], fontsize=11)
        ax.tick_params(axis='y', labelsize=11)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Remover subplots vazios, se houver
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Criar uma única legenda para todo o gráfico
    handles, labels = [], []
    # Usar um conjunto para garantir rótulos únicos
    unique_labels = set()
    for ax_item in fig.get_axes():
        if ax_item and ax_item.lines:
            for line in ax_item.lines:
                label = line.get_label()
                if label not in unique_labels and label != '_nolegend_':
                    handles.append(line)
                    labels.append(label)
                    unique_labels.add(label)
    
    # Ordenar a legenda pelos anos
    sorted_labels_handles = sorted(zip(labels, handles), key=lambda x: int(x[0]))
    sorted_labels = [label for label, handle in sorted_labels_handles]
    sorted_handles = [handle for label, handle in sorted_labels_handles]

    if sorted_handles and sorted_labels:
        fig.legend(sorted_handles, sorted_labels, title='Ano', loc='upper right', bbox_to_anchor=(1.0, 1.0),
                   fontsize=12, title_fontsize='14', frameon=True, fancybox=True, shadow=True, ncol=1)

    plt.tight_layout(rect=[0, 0, 0.98, 0.98]) # Ajusta para acomodar a legenda e o título
    st.pyplot(fig)

    # --- Análise e Insights ---
    st.markdown("---")
    st.markdown("<h2 class='section-header'>💡 Seus Insights Climáticos: O Que os Dados Revelam?</h2>", unsafe_allow_html=True)
    st.markdown("""
    Este painel não é apenas um conjunto de gráficos; é uma **janela interativa** para o comportamento climático dinâmico das regiões brasileiras.
    Use os filtros na barra lateral para moldar sua narrativa e descobrir padrões que podem ser cruciais para diversos setores,
    como agricultura, gestão de recursos hídricos, planejamento urbano e muito mais!
    """)
    
    st.markdown("### 🎯 Guiando Sua Análise Profunda:")
    st.markdown("""
    * **Padrões Sazonais Clássicos:** Observe como a linha de cada ano (e de cada variável) sobe e desce ao longo dos meses. Isso reflete as estações do ano e suas características climáticas inerentes. Por exemplo, note os picos de chuva no verão do Sudeste ou o período mais seco no Centro-Oeste.
    * **Diferenças Regionais Marcantes:** Compare os gráficos entre as diferentes regiões. Qual região exibe a temperatura mais estável durante o ano? Qual delas possui a maior amplitude na precipitação? Essas distinções são fundamentalmente moldadas pela geografia única e pelos sistemas climáticos atuantes em cada área do Brasil.
    * **Variabilidade Interanual e Eventos Extremos:** Ao selecionar e comparar diferentes anos, preste atenção em como um mesmo mês pode apresentar valores muito distintos entre um ano e outro. Isso é a **variabilidade climática interanual**, e anos com desvios significativos podem indicar a ocorrência de fenômenos climáticos notáveis, como:
        * 🔥 **Ondas de Calor/Frio Incomuns:** Picos ou vales extremos de temperatura.
        * 💧 **Secas Severas/Inundações:** Meses com precipitação drasticamente abaixo ou muito acima da média histórica.
        * ☀️ **Anomalias de Radiação Solar:** Períodos com incidência solar atípica (excesso de sol resultando em mais calor e evaporação, ou excesso de nebulosidade).
    """)
    
    st.markdown("### 💭 Sua Tarefa:")
    st.markdown("""
    Ao explorar os dados, faça-se perguntas instigantes:
    * "*Há algum ano que se destaca de forma inusitada em uma região específica para a variável que estou analisando?*"
    * "*As tendências observadas em uma variável (ex: temperatura) parecem se correlacionar com as de outra (ex: precipitação)?*"
    * "*O que esses padrões e desvios significam para a **sustentabilidade**, a **economia** e a **vida** nas regiões do Brasil?*"
    """)

    # --- Análise de Extremos de Radiação (com emojis e melhor formatação) ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.markdown("---")
        st.markdown("<h2 class='section-header'>⚡ Foco Especial: Análise de Extremos de Radiação Global</h2>", unsafe_allow_html=True)
        st.markdown("""
        A radiação solar é uma variável climática de **extrema importância**. Ao focar nela, podemos identificar os momentos de maior e menor incidência solar,
        que são cruciais para setores como **energia fotovoltaica**, **agricultura** e para entender **eventos de seca** ou **excessiva nebulosidade**.
        """)

        # Filtra apenas os anos selecionados para a análise de extremos
        df_analise_extremos = df_unificado[df_unificado['Ano'].isin(anos_selecionados)]

        if coluna_var in df_analise_extremos.columns and not df_analise_extremos[coluna_var].empty and df_analise_extremos[coluna_var].max() > 0:
            # Identifica o maior valor de radiação global
            idx_max = df_analise_extremos[coluna_var].idxmax()
            max_rad_data = df_analise_extremos.loc[idx_max]

            # Identifica o menor valor de radiação global (apenas valores > 0 para evitar leituras de sensores off)
            # Garante que há valores válidos antes de tentar min
            min_valid_df = df_analise_extremos[df_analise_extremos[coluna_var] > 0]
            
            if not min_valid_df.empty:
                min_valid_rad = min_valid_df[coluna_var].min()
                idx_min_valid = min_valid_df[min_valid_df[coluna_var] == min_valid_rad].index[0]
                min_rad_data = df_analise_extremos.loc[idx_min_valid]

                col_max, col_min = st.columns(2)

                with col_max:
                    st.markdown(f"""
                    <div style="background-color:#ffe0b2; padding: 25px; border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                        <h4 style="color:#e65100;">☀️ Raio de Sol Mais Intenso Registrado</h4>
                        <p style="font-size:1.15em; color:#424242;">O **maior valor** de Radiação Global no período selecionado foi de:</p>
                        <p style="font-size:1.8em; font-weight:bold; color:#f57c00; margin-top: 10px; margin-bottom: 10px;">{max_rad_data[coluna_var]:.2f} Kj/m²</p>
                        <ul style="list-style-type: none; padding: 0;">
                            <li><span style="font-weight:bold; color:#333;">Região:</span> {max_rad_data['Regiao']}</li>
                            <li><span style="font-weight:bold; color:#333;">Mês:</span> {int(max_rad_data['Mês']):02d}</li>
                            <li><span style="font-weight:bold; color:#333;">Ano:</span> {int(max_rad_data['Ano'])}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                with col_min:
                    st.markdown(f"""
                    <div style="background-color:#bbdefb; padding: 25px; border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                        <h4 style="color:#0d47a1;">☁️ Período de Menos Luz Solar (Excluindo Zeros)</h4>
                        <p style="font-size:1.15em; color:#424242;">O **menor valor significativo** de Radiação Global no período selecionado foi de:</p>
                        <p style="font-size:1.8em; font-weight:bold; color:#1976d2; margin-top: 10px; margin-bottom: 10px;">{min_rad_data[coluna_var]:.2f} Kj/m²</p>
                        <ul style="list-style-type: none; padding: 0;">
                            <li><span style="font-weight:bold; color:#333;">Região:</span> {min_rad_data['Regiao']}</li>
                            <li><span style="font-weight:bold; color:#333;">Mês:</span> {int(min_rad_data['Mês']):02d}</li>
                            <li><span style="font-weight:bold; color:#333;">Ano:</span> {int(min_rad_data['Ano'])}</li>
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
                 st.info("ℹ️ Não há dados de Radiação Global significativos (>0) para os anos selecionados para realizar a análise de extremos.")
        else:
            st.info("ℹ️ Dados de Radiação Global não disponíveis ou insuficientes para uma análise significativa de extremos para a variável selecionada e anos filtrados.")

except FileNotFoundError:
    st.error(f"❌ **Erro Crítico:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo na pasta `medias`.")
    st.info("💡 **Dica:** Certifique-se de que o arquivo `medias_mensais_geo_2020_2025.csv` está localizado corretamente na pasta `medias` dentro do seu projeto.")
except KeyError as e:
    st.error(f"❌ **Erro de Dados:** A coluna esperada '{e}' não foi encontrada no arquivo CSV ou não pôde ser calculada. Verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média.")
    st.info("💡 **Dica:** O arquivo CSV deve conter colunas como 'Regiao', 'Ano', 'Mês', e, para temperatura média, 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' ou já ter uma coluna 'Temperatura Média (°C)'. As colunas de precipitação e radiação devem ser 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' e 'RADIACAO GLOBAL (Kj/m²)'.")
except Exception as e:
    st.error(f"💥 **Ops! Ocorreu um erro inesperado:** {e}")
    st.warning("🔄 **Sugestão:** Tente recarregar a página. Se o problema persistir, pode ser um erro nos dados ou no script. Por favor, entre em contato com o desenvolvedor se necessário.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9em; margin-top: 30px;">
    Desenvolvido com 💙 e dados abertos para o conhecimento climático. <br>
    [Ana Sophia e Igor Andrade] © 2025
</div>
""", unsafe_allow_html=True)
