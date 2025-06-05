import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# Caminho relativo ao arquivo CSV dentro do projeto
# Certifique-se de que o arquivo 'medias_mensais_geo_2020_2025.csv'
# esteja no subdiretório 'medias' em relação ao script Python.
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- ALTERAÇÃO AQUI: Novo título principal do aplicativo ---
st.title("Radiação Global por Estação (2020-2025)")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Calcular a média da temperatura se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns:
        df_unificado['Temperatura Média (°C)'] = (
            df_unificado['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df_unificado['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    elif 'Temperatura Média (°C)' not in df_unificado.columns:
        pass 

    # Certificar-se de que a coluna 'Mês' é numérica
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado = df_unificado.dropna(subset=['Mês'])

    # Lista de regiões e anos únicas
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Variáveis a serem plotadas
    variaveis = {
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }

    # Seleção interativa da variável, com 'Radiação Global (Kj/m²)' como padrão
    if 'Radiação Global (Kj/m²)' in variaveis:
        default_var_index = list(variaveis.keys()).index('Radiação Global (Kj/m²)')
    else:
        default_var_index = 0

    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()), index=default_var_index)
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    cmap = plt.get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Gráfico facetado por região
    st.subheader(f"Média Mensal de {nome_var} por Região (2020-2025)") # Subtítulo do gráfico principal
    
    n_cols = 3
    n_rows = int(np.ceil(len(regioes) / n_cols))
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(5*n_cols, 4*n_rows), sharey=True)
    
    if n_rows * n_cols > 1:
        axes = axes.flatten()
    elif len(regioes) == 1:
        axes = [axes]

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        for ano in anos:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty:
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        ax.set_title(regiao)
        ax.set_xlabel('Mês')
        if i % n_cols == 0:
            ax.set_ylabel(nome_var)
        ax.set_xticks(meses)
        ax.grid(True)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    handles, labels = [], []
    for ax_item in axes:
        if ax_item and ax_item.lines:
            handles, labels = ax_item.get_legend_handles_labels()
            if handles:
                break
            
    if handles and labels:
        fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.05, 1))

    plt.tight_layout(rect=[0, 0, 0.95, 1])
    st.pyplot(fig)

    # --- Análise de Extremos de Radiação ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.subheader("Análise dos Extremos de Radiação Global (2020-2025)") # Subtítulo da seção de extremos

        if coluna_var in df_unificado.columns and not df_unificado[coluna_var].empty:
            idx_max = df_unificado[coluna_var].idxmax()
            max_rad_data = df_unificado.loc[idx_max]

            idx_min = df_unificado[coluna_var].idxmin()
            min_rad_data = df_unificado.loc[idx_min]

            st.markdown(f"""
            ### Maiores Valores de Radiação Global

            O maior valor de Radiação Global registrado no período de 2020 a 2025 foi de **{max_rad_data[coluna_var]:.2f} Kj/m²**.
            * **Região:** {max_rad_data['Regiao']}
            * **Mês:** {max_rad_data['Mês']}
            * **Ano:** {max_rad_data['Ano']}
            """)

            st.markdown(f"""
            ### Menores Valores de Radiação Global

            O menor valor de Radiação Global registrado no período de 2020 a 2025 foi de **{min_rad_data[coluna_var]:.2f} Kj/m²**.
            * **Região:** {min_rad_data['Regiao']}
            * **Mês:** {min_rad_data['Mês']}
            * **Ano:** {min_rad_data['Ano']}
            """)

            st.markdown("""
            ### Relevância dos Extremos de Radiação Global

            A identificação de picos e vales na radiação global é crucial por diversas razões:

            * **Geração de Energia Solar:** Períodos de alta radiação são ideais para a geração de energia fotovoltaica, indicando regiões e épocas do ano de
