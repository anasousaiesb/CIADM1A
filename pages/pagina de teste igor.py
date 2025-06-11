import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide", page_title="Análise Climática Interativa 🌐🌡️")

# CSS para estilização aprimorada
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Poppins', sans-serif;
    color: #333333; /* Cor de texto padrão mais suave */
}

.stApp {
    background: linear-gradient(to right bottom, #e0f2f7, #ffffff); /* Gradiente suave de azul claro para branco */
}

.main-title-5 {
    font-size: 3.8em; /* Tamanho maior para o título principal */
    font-weight: 700;
    color: #007BFF; /* Azul vibrante */
    text-align: center;
    margin-bottom: 0.2em; /* Espaçamento menor */
    text-shadow: 3px 3px 6px rgba(0,0,0,0.15); /* Sombra mais pronunciada */
    letter-spacing: 1px; /* Leve espaçamento entre letras */
}
.subtitle-5 {
    font-size: 1.8em; /* Subtítulo um pouco maior */
    color: #28A745; /* Verde para contrastar e remeter a natureza/clima */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 2em; /* Mais espaçamento abaixo */
    font-weight: 600;
}
.header-section-5 {
    background: linear-gradient(135deg, #BBDEFB 0%, #90CAF9 100%); /* Gradiente azul claro/médio para o cabeçalho */
    padding: 2.5em; /* Mais preenchimento */
    border-radius: 20px; /* Bordas mais arredondadas */
    margin-bottom: 2.5em; /* Mais espaçamento inferior */
    box-shadow: 0 10px 25px rgba(0,0,0,0.2); /* Sombra mais forte */
    border: 2px solid #64B5F6; /* Borda sutil */
}

.stSidebar .stSelectbox, .stSidebar .stMultiSelect {
    font-weight: 600;
    color: #0056b3; /* Cor de texto para os labels do sidebar */
}

h2 {
    color: #0056b3; /* Azul escuro para títulos de seção */
    border-bottom: 2px solid #ADD8E6; /* Linha sutil abaixo dos títulos */
    padding-bottom: 0.5em;
    margin-top: 2em;
}

.stInfo {
    background-color: #e0f7fa; /* Fundo mais suave para st.info */
    border-left: 5px solid #00BCD4; /* Borda de destaque */
    padding: 1em;
    border-radius: 8px;
}

.stWarning {
    background-color: #fff3cd;
    border-left: 5px solid #ffc107;
    padding: 1em;
    border-radius: 8px;
}

.stButton>button {
    background-color: #28a745;
    color: white;
    border-radius: 8px;
    padding: 0.5em 1em;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --- OTIMIZAÇÃO: Função para carregar e cachear os dados ---
@st.cache_data
def carregar_dados(caminho):
    """
    Carrega os dados do arquivo CSV, realiza cálculos iniciais e o retorna.
    O uso de @st.cache_data acelera o app, evitando recarregar o arquivo a cada interação.
    """
    df = pd.read_csv(caminho)
    # Calcula a média da temperatura se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temperatura Média (°C)'] = (
            df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    # Garante que as colunas importantes são numéricas
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano', 'Regiao'])
    return df

try:
    # Caminho relativo ao arquivo CSV
    caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- TÍTULO PRINCIPAL ATRAENTE ---
    st.markdown('<div class="header-section-5">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title-5">Análise Climática Interativa por Região 🌐🌡️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-5">Desvende os Padrões Climáticos do Brasil (2020-2025)! 🇧🇷✨</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- MELHORIA: Filtros interativos na barra lateral ---
    st.sidebar.header("Filtros de Visualização 🔍")

    # Listas para os filtros
    regioes_disponiveis = sorted(df_unificado['Regiao'].unique())
    anos_disponiveis = sorted(df_unificado['Ano'].unique().astype(int))

    # Filtro de Regiões
    regioes_selecionadas = st.sidebar.multiselect(
        "Selecione as Regiões:",
        options=regioes_disponiveis,
        default=regioes_disponiveis[:2]  # Seleciona as duas primeiras regiões por padrão
    )

    # Filtro de Anos
    anos_selecionados = st.sidebar.multiselect(
        "Selecione os Anos:",
        options=anos_disponiveis,
        default=anos_disponiveis # Todos os anos selecionados por padrão
    )
    
    # Filtro de Variável
    variaveis = {
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)',
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
    }
    nome_var = st.sidebar.selectbox(
        "Selecione a Variável:",
        options=list(variaveis.keys())
    )
    coluna_var = variaveis[nome_var]

    # Validação para evitar erros se nenhuma região ou ano for selecionado
    if not regioes_selecionadas or not anos_selecionados:
        st.warning("Por favor, selecione **pelo menos uma região e um ano** para exibir os dados. ⚠️")
        st.stop()
    
    # Validação da existência da coluna da variável
    if coluna_var not in df_unificado.columns:
        st.error(f"A coluna **'{coluna_var}'** para a variável **'{nome_var}'** não foi encontrada no arquivo. Verifique se o nome está correto. 😔")
        st.stop()

    # Filtra o DataFrame principal com base nas seleções do usuário
    df_filtrado = df_unificado[
        df_unificado['Regiao'].isin(regioes_selecionadas) &
        df_unificado['Ano'].isin(anos_selecionados)
    ]

    # --- Gráfico Principal ---
    st.header(f"Tendências Mensais de {nome_var} por Região 📈")
    st.markdown(f"""
        Explore como a **{nome_var}** varia ao longo dos meses em diferentes regiões do Brasil.
        Cada linha no gráfico representa um ano diferente, permitindo identificar padrões sazonais e anomalias.
        Use os filtros na barra lateral para personalizar sua análise!
    """)

    # --- ALTERAÇÃO: Cor do gráfico modificada para 'plasma' ---
    cmap = plt.get_cmap('viridis') # Mudei para viridis, que é mais acessível e agradável
    cores_anos = {ano: cmap(i / len(anos_selecionados)) for i, ano in enumerate(anos_selecionados)}

    # Criação do grid de gráficos dinamicamente
    n_cols = 3
    n_rows = int(np.ceil(len(regioes_selecionadas) / n_cols))
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(5 * n_cols, 4 * n_rows), sharey=True, squeeze=False)
    axes = axes.flatten()

    for i, regiao in enumerate(regioes_selecionadas):
        ax = axes[i]
        df_regiao_filtrada = df_filtrado[df_filtrado['Regiao'] == regiao]
        for ano in anos_selecionados:
            df_ano_regiao = df_regiao_filtrada[df_regiao_filtrada['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
            if not df_ano_regiao.empty:
                ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        ax.set_title(regiao, fontsize=14, color='#333333') # Cor do título do subplot
        ax.set_xlabel('Mês', fontsize=10)
        if i % n_cols == 0:
            ax.set_ylabel(nome_var, fontsize=10)
        ax.set_xticks(range(1, 13))
        ax.grid(True, linestyle='--', alpha=0.6)

    # Remove eixos vazios
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Criação da legenda unificada
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.08, 0.95)) # Ajuste da posição da legenda
    plt.tight_layout(rect=[0, 0, 0.95, 1]) # Ajuste do layout para acomodar a legenda
    st.pyplot(fig)

    # --- Seções de Análise (só aparecem se a variável for Radiação Global) ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.markdown("---")
        st.header("Análise Detalhada da Radiação Global ☀️")
        st.markdown("""
            Mergulhe mais fundo nos dados de **Radiação Global**!
            Aqui você encontra os valores extremos registrados e a média sazonal, revelando insights cruciais.
        """)

        col1, col2 = st.columns(2)

        with col1:
            # Análise de Extremos
            st.subheader("Extremos de Radiação (Período Selecionado) 🚀")
            if not df_filtrado[coluna_var].empty:
                idx_max = df_filtrado[coluna_var].idxmax()
                max_rad_data = df_filtrado.loc[idx_max]

                idx_min = df_filtrado[coluna_var].idxmin()
                min_rad_data = df_filtrado.loc[idx_min]
                
                st.info(f"**Máximo Registrado:** **{max_rad_data[coluna_var]:.2f} Kj/m²**\n"
                                f"📍 {max_rad_data['Regiao']}, Mês {int(max_rad_data['Mês'])}, Ano {int(max_rad_data['Ano'])}")

                st.info(f"**Mínimo Registrado:** **{min_rad_data[coluna_var]:.2f} Kj/m²**\n"
                                f"📍 {min_rad_data['Regiao']}, Mês {int(min_rad_data['Mês'])}, Ano {int(min_rad_data['Ano'])}")
            else:
                st.write("Dados insuficientes para análise de extremos. 😔")

        with col2:
            # Análise Sazonal
            st.subheader("Média Sazonal de Radiação 🏖️❄️")
            meses_verao = [12, 1, 2] # Verão no Hemisfério Sul
            meses_inverno = [6, 7, 8] # Inverno no Hemisfério Sul
            
            dados_sazonais = []
            for regiao in regioes_selecionadas:
                df_regiao_sazonal = df_filtrado[df_filtrado['Regiao'] == regiao]
                media_verao = df_regiao_sazonal[df_regiao_sazonal['Mês'].isin(meses_verao)][coluna_var].mean()
                media_inverno = df_regiao_sazonal[df_regiao_sazonal['Mês'].isin(meses_inverno)][coluna_var].mean()
                dados_sazonais.append({
                    'Região': regiao,
                    'Média Verão (Kj/m²)': media_verao,
                    'Média Inverno (Kj/m²)': media_inverno
                })
            
            df_sazonais = pd.DataFrame(dados_sazonais)
            st.dataframe(df_sazonais.round(2))

        st.markdown("---")
        st.header("Por Que a Radiação Solar Importa? 💡")
        st.markdown("""
            A radiação solar é um fator climático fundamental com vastas implicações:

            -   **Energia Solar Sustentável:** Regiões com **picos de radiação** oferecem alto potencial para a instalação de painéis fotovoltaicos, impulsionando a **geração de energia limpa**.
            -   **Vital para a Agricultura:** É a força motriz da **fotossíntese**, essencial para o crescimento das plantas. No entanto, o **excesso de radiação** pode levar a estresse hídrico e queima de culturas.
            -   **Impacto no Clima e Meio Ambiente:** A radiação influencia diretamente a **temperatura** do ar e do solo, a **evaporação** de rios e reservatórios, e pode contribuir para a formação de **ilhas de calor urbanas**, afetando o bem-estar das cidades.

            Entender esses padrões é crucial para o planejamento energético, agrícola e urbano do Brasil!
        """)

except FileNotFoundError:
    st.error(f"Erro: O arquivo **'{caminho_arquivo_unificado}'** não foi encontrado. Por favor, verifique o caminho e a localização do arquivo em seu projeto. 😔")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao carregar ou processar os dados: **{e}** 🐛 Por favor, tente novamente ou contate o suporte.")

st.markdown("---")
st.write("Feito com ❤️ para uma análise climática mais inteligente.")
