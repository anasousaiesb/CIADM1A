import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# Caminho relativo ao arquivo CSV dentro do projeto
# Certifique-se de que o arquivo 'medias_mensais_geo_2020_2025.csv'
# esteja no subdiretório 'medias' em relação ao script Python.
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Médias Mensais Regionais (2020-2025) - Facetado por Região e Variável")

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
    st.subheader(f"Média Mensal de {nome_var} por Região (2020-2025)")
    
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
        st.subheader("Análise dos Extremos de Radiação Global (2020-2025)")

        # Garante que a coluna de radiação existe e não está vazia
        if coluna_var in df_unificado.columns and not df_unificado[coluna_var].empty:
            # Identifica o maior valor de radiação global
            idx_max = df_unificado[coluna_var].idxmax()
            max_rad_data = df_unificado.loc[idx_max]

            # Identifica o menor valor de radiação global (ignorando NaN)
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

            * **Geração de Energia Solar:** Períodos de alta radiação são ideais para a geração de energia fotovoltaica, indicando regiões e épocas do ano de maior potencial para projetos solares. Valores baixos, por outro lado, sinalizam menor eficiência.
            * **Agricultura:** A radiação solar é vital para a fotossíntese. Picos de radiação, especialmente se combinados com temperaturas elevadas e baixa umidade, podem causar estresse térmico e hídrico nas plantas. Períodos de baixa radiação podem limitar o crescimento e a produtividade das culturas.
            * **Clima e Qualidade do Ar:** A radiação afeta a temperatura do solo e do ar, influenciando a dinâmica atmosférica. Baixos níveis de radiação podem estar associados a maior nebulosidade ou poluição, enquanto altos níveis (especialmente em regiões urbanas) podem intensificar fenômenos como ilhas de calor e a formação de ozônio troposférico.
            * **Recursos Hídricos:** Alta radiação contribui para a evaporação da água, impactando o nível de rios e reservatórios, especialmente em períodos de seca.

            Esses dados fornecem insights valiosos para o planejamento energético, agrícola e ambiental, permitindo a otimização de recursos e a mitigação de riscos climáticos.
            """)
        else:
            st.write("Dados de Radiação Global não disponíveis ou insuficientes para análise de extremos.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
