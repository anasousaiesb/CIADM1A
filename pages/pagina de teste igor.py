import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# --- Título principal mais descritivo ---
st.title("Análise Climática Interativa por Região (2020-2025)")

# --- Função para carregar e cachear os dados ---
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

    # --- Filtros interativos na barra lateral ---
    st.sidebar.header("Filtros de Visualização")

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
        st.warning("Por favor, selecione pelo menos uma região e um ano para continuar.")
        st.stop()
    
    # Validação da existência da coluna da variável
    if coluna_var not in df_unificado.columns:
        st.error(f"A coluna '{coluna_var}' para a variável '{nome_var}' não foi encontrada no arquivo.")
        st.stop()

    # Filtra o DataFrame principal com base nas seleções do usuário
    df_filtrado = df_unificado[
        df_unificado['Regiao'].isin(regioes_selecionadas) &
        df_unificado['Ano'].isin(anos_selecionados)
    ]

    # --- Gráfico Principal ---
    st.header(f"Média Mensal de {nome_var}")

    # --- Cor do gráfico modificada para 'plasma' ---
    cmap = plt.get_cmap('plasma')
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
        ax.set_title(regiao, fontsize=14)
        ax.set_xlabel('Mês')
        if i % n_cols == 0:
            ax.set_ylabel(nome_var)
        ax.set_xticks(range(1, 13))
        ax.grid(True, linestyle='--', alpha=0.6)

    # Remove eixos vazios
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Criação da legenda unificada
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title='Ano', loc='upper right')
    plt.tight_layout(rect=[0, 0, 0.95, 1])
    st.pyplot(fig)

    # --- Seções de Análise (só aparecem se a variável for Radiação Global) ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.markdown("---")
        st.header("Análise Detalhada da Radiação Global")

        col1, col2 = st.columns(2)

        with col1:
            # Análise de Extremos
            st.subheader("Extremos de Radiação")
            if not df_filtrado[coluna_var].empty:
                idx_max = df_filtrado[coluna_var].idxmax()
                max_rad_data = df_filtrado.loc[idx_max]

                idx_min = df_filtrado[coluna_var].idxmin()
                min_rad_data = df_filtrado.loc[idx_min]
                
                st.info(f"**Máximo:** **{max_rad_data[coluna_var]:.2f} Kj/m²**\n"
                                  f"({max_rad_data['Regiao']}, Mês {int(max_rad_data['Mês'])}, Ano {int(max_rad_data['Ano'])})")

                st.info(f"**Mínimo:** **{min_rad_data[coluna_var]:.2f} Kj/m²**\n"
                                  f"({min_rad_data['Regiao']}, Mês {int(min_rad_data['Mês'])}, Ano {int(min_rad_data['Ano'])})")
            else:
                st.write("Dados insuficientes para análise de extremos.")

        with col2:
            # Análise Sazonal
            st.subheader("Média por Estação")
            meses_verao = [12, 1, 2]
            meses_inverno = [6, 7, 8]
            
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

        st.markdown("""
        ### Relevância da Radiação Solar
        - **Energia Solar:** Picos de radiação indicam alto potencial para geração fotovoltaica.
        - **Agricultura:** A radiação é vital para a fotossíntese, mas em excesso pode causar estresse hídrico.
        - **Clima:** Influencia a temperatura, a evaporação de reservatórios e a formação de ilhas de calor urbanas.
        """)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
