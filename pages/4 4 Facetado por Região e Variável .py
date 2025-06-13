import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide", page_title="Análise Climática Interativa por Região ☀️")

# CSS para estilização aprimorada do título
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fa; /* Fundo suave para o aplicativo */
}
.main-title {
    font-size: 3.5em;
    font-weight: 700;
    color: #2E8B57; /* Um verde mais escuro e atraente */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle {
    font-size: 1.8em;
    color: #3CB371; /* Um verde um pouco mais claro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section {
    background-color: #e6f7ee; /* Fundo levemente verde para a seção de cabeçalho */
    padding: 1.5em;
    border-radius: 10px;
    margin-bottom: 2em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
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
    # Carregar os dados
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- TÍTULO PRINCIPAL E SUBTÍTULO COM EMOJIS (APLICANDO O DESIGN DO PRIMEIRO CÓDIGO) ---
    st.markdown('<div class="header-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Análise Climática Interativa por Região 🌎☀️📊</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explorando Padrões Climáticos no Brasil (2020-2025) 🇧🇷</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("""
    Este aplicativo Streamlit permite uma exploração detalhada de variáveis climáticas
    como **Temperatura Média**, **Radiação Global** e **Precipitação Total**
    para as regiões do Brasil entre 2020 e 2025.
    """)

    # --- Filtros interativos na barra lateral ---
    st.sidebar.header("⚙️ Ajuste sua Análise Aqui:")

    # Listas para os filtros
    regioes_disponiveis = sorted(df_unificado['Regiao'].unique())
    anos_disponiveis = sorted(df_unificado['Ano'].unique().astype(int))

    # Filtro de Regiões
    regioes_selecionadas = st.sidebar.multiselect(
        "📍 Selecione as Regiões de Interesse:",
        options=regioes_disponiveis,
        default=regioes_disponiveis[:2]  # Seleciona as duas primeiras regiões por padrão
    )

    # Filtro de Anos
    anos_selecionados = st.sidebar.multiselect(
        "📅 Escolha os Anos para Comparar:",
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
        "📊 Qual Variável Climática Deseja Visualizar?",
        options=list(variaveis.keys())
    )
    coluna_var = variaveis[nome_var]

    # Validação para evitar erros se nenhuma região ou ano for selecionado
    if not regioes_selecionadas or not anos_selecionados:
        st.warning("⚠️ **Ops!** Parece que você esqueceu de selecionar uma região ou um ano. Por favor, escolha pelo menos um de cada para iniciarmos a análise. ⏳")
        st.stop()
    
    # Validação da existência da coluna da variável
    if coluna_var not in df_unificado.columns:
        st.error(f"❌ **Erro:** A coluna '{coluna_var}' para a variável '{nome_var}' não foi encontrada nos dados. Por favor, verifique o arquivo CSV. 😬")
        st.stop()

    # Filtra o DataFrame principal com base nas seleções do usuário
    df_filtrado = df_unificado[
        df_unificado['Regiao'].isin(regioes_selecionadas) &
        df_unificado['Ano'].isin(anos_selecionados)
    ]

    # --- Gráfico Principal ---
    st.markdown("---")
    st.header(f"📈 Tendência Mensal de {nome_var} por Região e Ano")
    st.markdown(f"Explore como a **{nome_var.lower()}** se comporta ao longo dos meses para as regiões e anos selecionados. Cada linha representa um ano, permitindo uma comparação clara das tendências sazonais.")

    # --- Cor do gráfico modificada para 'plasma' ---
    cmap = plt.get_cmap('viridis') # 'viridis' é uma boa alternativa para 'plasma' e mais acessível
    cores_anos = {ano: cmap(i / len(anos_selecionados)) for i, ano in enumerate(anos_selecionados)}

    # Criação do grid de gráficos dinamicamente
    n_cols = 2 if len(regioes_selecionadas) > 1 else 1 # Ajusta o número de colunas
    if len(regioes_selecionadas) > 4: # Para muitas regiões, use 3 colunas
        n_cols = 3
    
    n_rows = int(np.ceil(len(regioes_selecionadas) / n_cols))
    
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(7 * n_cols, 5 * n_rows), sharey=True, squeeze=False)
    axes = axes.flatten()

    for i, regiao in enumerate(regioes_selecionadas):
        ax = axes[i]
        df_regiao_filtrada = df_filtrado[df_filtrado['Regiao'] == regiao]
        for ano in anos_selecionados:
            df_ano_regiao = df_regiao_filtrada[df_regiao_filtrada['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
            if not df_ano_regiao.empty:
                ax.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano), linewidth=2, markersize=6)
        ax.set_title(f"Região: {regiao}", fontsize=14, fontweight='bold')
        ax.set_xlabel('Mês do Ano')
        if i % n_cols == 0:
            ax.set_ylabel(nome_var, fontsize=12)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.tick_params(axis='both', which='major', labelsize=10)

    # Remove eixos vazios
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Criação da legenda unificada
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.0, 1.0), ncol=1, fancybox=True, shadow=True)
    plt.tight_layout(rect=[0, 0, 0.9, 1]) # Ajusta o layout para a legenda
    st.pyplot(fig)
    st.markdown("---")

    # --- Seções de Análise (só aparecem se a variável for Radiação Global) ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.header("insights sobre Radiação Global ☀️")
        st.markdown("A radiação solar é uma métrica crucial! Vamos entender seus picos e vales, e como ela se distribui ao longo das estações.")

        col1, col2 = st.columns(2)

        with col1:
            # Análise de Extremos
            st.subheader("Extremos de Radiação Detectados 🚀")
            if not df_filtrado[coluna_var].empty:
                idx_max = df_filtrado[coluna_var].idxmax()
                max_rad_data = df_filtrado.loc[idx_max]

                idx_min = df_filtrado[coluna_var].idxmin()
                min_rad_data = df_filtrado.loc[idx_min]
                
                st.markdown(f"**Maior Radiação Registrada:**\n"
                                f"**{max_rad_data[coluna_var]:.2f} Kj/m²** 🤯\n"
                                f"📍 Região: **{max_rad_data['Regiao']}**\n"
                                f"🗓️ Mês: **{int(max_rad_data['Mês'])}**\n"
                                f"🗓️ Ano: **{int(max_rad_data['Ano'])}**")

                st.markdown(f"**Menor Radiação Registrada:**\n"
                                f"**{min_rad_data[coluna_var]:.2f} Kj/m²** 🥶\n"
                                f"📍 Região: **{min_rad_data['Regiao']}**\n"
                                f"🗓️ Mês: **{int(min_rad_data['Mês'])}**\n"
                                f"🗓️ Ano: **{int(min_rad_data['Ano'])}**")
            else:
                st.info("Não há dados suficientes para analisar os extremos de radiação para a sua seleção. 😔")

        with col2:
            # Análise Sazonal
            st.subheader("Média por Estação (Verão vs. Inverno) 🌡️")
            meses_verao = [12, 1, 2] # Considerando o verão no hemisfério sul
            meses_inverno = [6, 7, 8] # Considerando o inverno no hemisfério sul
            
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
            if not df_sazonais.empty:
                st.dataframe(df_sazonais.round(2).style.highlight_max(subset=['Média Verão (Kj/m²)', 'Média Inverno (Kj/m²)'], axis=1, color='lightgreen').highlight_min(subset=['Média Verão (Kj/m²)', 'Média Inverno (Kj/m²)'], axis=1, color='salmon'))
            else:
                st.info("Não foi possível calcular as médias sazonais com os dados selecionados. 🙁")

        st.markdown("---")
        st.subheader("Por que a Radiação Solar Importa? 💡")
        st.markdown("""
        A **radiação solar** é muito mais do que apenas luz do sol! Ela é um motor para diversos aspectos:

        * **Energia Solar Sustentável:** Regiões com alta radiação são ideais para a instalação de painéis fotovoltaicos, convertendo a luz do sol em eletricidade limpa e renovável. 🌞 Potencial máximo!
        * **Agricultura e Produção de Alimentos:** Essencial para a **fotossíntese**, a radiação solar impulsiona o crescimento das plantas. Conhecer seus níveis ajuda a otimizar o plantio e a irrigação, evitando estresse nas culturas. 🌾
        * **Impacto no Clima e Meio Ambiente:** A radiação influencia diretamente a **temperatura** (calor), a **evaporação** de rios e reservatórios e até a formação de **ilhas de calor** em áreas urbanas. É um fator chave para entender as mudanças climáticas. 🌡️💧
        """)

except FileNotFoundError:
    st.error(f"❌ **Erro:** O arquivo de dados climáticos '{caminho_arquivo_unificado}' não foi encontrado. Por favor, certifique-se de que ele está na pasta 'medias' dentro do diretório do seu aplicativo. 🧐")
except Exception as e:
    st.error(f"💥 **Ocorreu um erro inesperado:** Parece que algo deu errado ao processar os dados. Por favor, tente novamente ou entre em contato com o suporte se o problema persistir. Detalhes do erro: `{e}`")

st.markdown("---")
st.markdown("Feito com ❤️ e dados climáticos para você explorar! Gostaria de analisar alguma outra variável ou período? ✨")
