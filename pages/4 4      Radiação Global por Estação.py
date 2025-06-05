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
    # Isso é importante para que 'Temperatura Média (°C)' esteja disponível
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns:
        df_unificado['Temperatura Média (°C)'] = (
            df_unificado['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df_unificado['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    # Caso a coluna 'Temperatura Média (°C)' já exista no CSV ou não seja selecionada,
    # não precisamos calcular, mas verificamos se existe para evitar KeyError.
    elif 'Temperatura Média (°C)' not in df_unificado.columns:
        # Se as colunas de max/min não estão lá e a coluna 'Temperatura Média (°C)'
        # também não, e o usuário tenta selecionar "Temperatura Média (°C)", isso falharia.
        # Por enquanto, vamos permitir que o Streamlit mostre o KeyError se acontecer.
        # Uma tratativa mais robusta seria remover 'Temperatura Média (°C)' das opções
        # de 'variaveis' se as colunas necessárias não existirem.
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
    # Verifica se 'Radiação Global (Kj/m²)' está nas chaves de variaveis para definir o índice
    if 'Radiação Global (Kj/m²)' in variaveis:
        default_var_index = list(variaveis.keys()).index('Radiação Global (Kj/m²)')
    else: # Se por algum motivo não tiver, pega o primeiro da lista
        default_var_index = 0

    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()), index=default_var_index)
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    cmap = plt.get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Gráfico facetado por região
    st.subheader(f"Média Mensal de {nome_var} por Região (2020-2025)")
    
    n_cols = 3 # Número de colunas no subplot
    n_rows = int(np.ceil(len(regioes) / n_cols))
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(5*n_cols, 4*n_rows), sharey=True)
    
    # Achata o array de eixos para facilitar a iteração se for 2D ou 1D com um único elemento
    if n_rows * n_cols > 1:
        axes = axes.flatten()
    elif len(regioes) == 1:
        axes = [axes] # Garante que axes seja uma lista mesmo para uma única região

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        for ano in anos:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty:
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        ax.set_title(regiao)
        ax.set_xlabel('Mês')
        if i % n_cols == 0: # Apenas para a primeira coluna de subplots
            ax.set_ylabel(nome_var)
        ax.set_xticks(meses)
        ax.grid(True)

    # Remove subplots vazios, se houver
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Adicionar legenda fora dos subplots
    handles, labels = [], []
    # Tenta pegar a legenda de um dos subplots que tenha linhas
    for ax_item in axes:
        if ax_item and ax_item.lines: # Verifica se o eixo existe e tem linhas
            handles, labels = ax_item.get_legend_handles_labels()
            if handles: # Se encontrou, pode parar
                break
            
    if handles and labels: # Apenas desenha a legenda se houver handles/labels
        fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.05, 1))

    plt.tight_layout(rect=[0, 0, 0.95, 1]) # Ajusta o layout para a legenda não sobrepor
    st.pyplot(fig)

    # --- Análise de Radiação por Estação ---
    if nome_var == 'Radiação Global (Kj/m²)':
        st.subheader("Análise da Radiação Global por Estação (2020-2025)")

        # Define os meses de verão e inverno para o Brasil
        # Verão: Dezembro (12), Janeiro (1), Fevereiro (2)
        # Inverno: Junho (6), Julho (7), Agosto (8)
        meses_verao = [12, 1, 2]
        meses_inverno = [6, 7, 8]

        dados_sazonais = []
        for regiao in regioes:
            df_regiao = df_unificado[df_unificado['Regiao'] == regiao]

            # Filtra e calcula a média para o verão
            df_verao = df_regiao[df_regiao['Mês'].isin(meses_verao)]
            media_verao = df_verao[coluna_var].mean()

            # Filtra e calcula a média para o inverno
            df_inverno = df_regiao[df_regiao['Mês'].isin(meses_inverno)]
            media_inverno = df_inverno[coluna_var].mean()

            dados_sazonais.append({'Região': regiao, 'Radiação Média Verão (Kj/m²)': media_verao, 'Radiação Média Inverno (Kj/m²)': media_inverno})

        df_sazonais = pd.DataFrame(dados_sazonais)
        st.dataframe(df_sazonais.round(2))

        st.markdown("""
        **Como isso se relaciona com a geografia de cada região:**

        * **Latitude:** Regiões mais próximas do Equador (como Norte e Nordeste) tendem a receber maior radiação solar ao longo do ano, com menor variação sazonal, pois o ângulo de incidência dos raios solares é mais direto e constante. Regiões mais afastadas do Equador (como Sul) apresentam maior variação entre as estações, com radiação menor no inverno e maior no verão.
        * **Nebulosidade/Precipitação:** A presença de nuvens e o regime de chuvas influenciam diretamente a radiação global. Regiões com maior nebulosidade ou períodos chuvosos mais intensos (como o Norte no verão) podem ter radiação global média menor, mesmo estando em baixas latitudes. Inversamente, regiões com estações secas bem definidas (como o Centro-Oeste no inverno) podem apresentar alta radiação global devido ao céu claro.
        * **Topografia e Elevação:** Embora não seja explicitamente visível nesses dados agregados, a topografia local e a elevação também podem influenciar a radiação solar recebida.

        A tabela acima permite observar diretamente essas variações e como elas se alinham com o conhecimento geográfico e climático do Brasil.
        """)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
