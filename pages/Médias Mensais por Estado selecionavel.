import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Médias Mensais por Estado (2020-2025)")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Lista de estados únicos disponíveis
    estados_disponiveis = sorted(df_unificado['Estado'].unique())

    # Seleção interativa do estado
    estado_selecionado = st.selectbox("Selecione o Estado:", estados_disponiveis)

    # Filtrar dados para o estado selecionado
    df_estado = df_unificado[df_unificado['Estado'] == estado_selecionado]

    # Lista de anos únicas no estado selecionado
    anos_estado = sorted(df_estado['Ano'].unique())
    meses = sorted(df_estado['Mês'].unique())

    # Variáveis a serem plotadas
    variaveis = {
        'Temperatura Média (°C)': 'Temp_Media',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }

    # Seleção interativa da variável
    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos_estado)) for i, ano in enumerate(anos_estado)}

    # Gerar o gráfico para a variável escolhida e estado selecionado
    st.subheader(f"Média Mensal de {nome_var} em {estado_selecionado} (2020-2025)")
    fig, ax = plt.subplots(figsize=(10, 6))
    for ano in anos_estado:
        df_ano_estado = df_estado[df_estado['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
        if not df_ano_estado.empty:
            ax.plot(meses, df_ano_estado.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))

    ax.set_title(f'Média Mensal de {nome_var} em {estado_selecionado} (2020-2025)')
    ax.set_xlabel('Mês')
    ax.set_ylabel(nome_var)
    ax.set_xticks(meses)
    ax.grid(True)
    ax.legend(title='Ano')
    plt.tight_layout()
    st.pyplot(fig)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
