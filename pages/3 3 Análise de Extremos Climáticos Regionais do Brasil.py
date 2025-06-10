import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Análise de Extremos Climáticos Regionais do Brasil (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)

    # Converte colunas para numérico, tratando erros
    for col in ['Mês', 'Ano', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
                'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
                'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
                'VENTO, RAJADA MAXIMA (m/s)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['Mês', 'Ano'])
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Visualização")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())

    # Dropdown para selecionar a variável de extremo
    variaveis_extremo = {
        'Temperatura Máxima (°C)': 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'Temperatura Mínima (°C)': 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Rajada Máxima de Vento (m/s)': 'VENTO, RAJADA MAXIMA (m/s)'
    }
    nome_var_extremo = st.sidebar.selectbox("Selecione a Variável de Extremo:", list(variaveis_extremo.keys()))
    coluna_var_extremo = variaveis_extremo[nome_var_extremo]
    unidade_var_extremo = nome_var_extremo.split('(')[-1].replace(')', '') if '(' in nome_var_extremo else ''

    # Slider para selecionar os anos
    ano_inicio, ano_fim = st.sidebar.select_slider(
        "Selecione o Intervalo de Anos:",
        options=anos,
        value=(min(anos), max(anos))
    )
    df_filtrado_ano = df_unificado[(df_unificado['Ano'] >= ano_inicio) & (df_unificado['Ano'] <= ano_fim)]

    st.markdown("---")

    # --- ANÁLISE DE EXTREMOS CLIMÁTICOS POR REGIÃO ---
    st.header(f"Análise de Extremos de {nome_var_extremo} por Região ({ano_inicio}-{ano_fim})")
    st.write(f"Esta seção apresenta os valores **máximos** (ou mínimos, para temperatura mínima) registrados para a variável selecionada em cada região, dentro do período de tempo escolhido.")

    # Agrupando por região para encontrar os valores extremos
    if "Mínima" in nome_var_extremo: # Para temperatura mínima, queremos o menor valor
        df_extremos_regionais = df_filtrado_ano.groupby('Regiao')[coluna_var_extremo].min().reset_index()
    else: # Para as outras variáveis, queremos o maior valor
        df_extremos_regionais = df_filtrado_ano.groupby('Regiao')[coluna_var_extremo].max().reset_index()

    if not df_extremos_regionais.empty:
        # Renomeando a coluna para melhor exibição
        df_extremos_regionais.rename(columns={coluna_var_extremo: f'{nome_var_extremo} Extremo'}, inplace=True)
        
        st.dataframe(df_extremos_regionais.sort_values(by=f'{nome_var_extremo} Extremo', ascending=False).set_index('Regiao').style.format("{:.2f}"))

        # Gráfico de barras para os extremos
        fig_extremo, ax_extremo = plt.subplots(figsize=(12, 6))
        ax_extremo.bar(df_extremos_regionais['Regiao'], df_extremos_regionais[f'{nome_var_extremo} Extremo'], color='skyblue')
        ax_extremo.set_title(f'{nome_var_extremo} Extremo por Região', fontsize=16)
        ax_extremo.set_xlabel('Região', fontsize=12)
        ax_extremo.set_ylabel(f'{nome_var_extremo} ({unidade_var_extremo})', fontsize=12)
        ax_extremo.tick_params(axis='x', rotation=45)
        ax_extremo.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_extremo)

        st.markdown("---")

        st.header("Insights e Hipóteses sobre Extremos Climáticos")
        st.warning("🚨 **Aviso:** As 'hipóteses' abaixo são exploratórias e baseadas em um período de dados limitado (2020-2025). Para conclusões definitivas sobre mudanças climáticas e eventos extremos, são necessárias séries históricas de dados muito mais longas.")

        if "Temperatura Máxima" in nome_var_extremo:
            st.markdown(f"**Observação:** A Região com o maior valor de **{nome_var_extremo}** ( {df_extremos_regionais.iloc[0]['Regiao']} com {df_extremos_regionais.iloc[0][f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) pode ser mais suscetível a **ondas de calor**.")
            st.markdown(f"**Hipótese:** Se a tendência de aumento das temperaturas máximas se mantiver, regiões que já registram valores elevados podem experimentar um **aumento na frequência e intensidade de eventos de calor extremo**, impactando a saúde pública, a agricultura e o consumo de energia.")
        elif "Temperatura Mínima" in nome_var_extremo:
            st.markdown(f"**Observação:** A Região com o menor valor de **{nome_var_extremo}** ( {df_extremos_regionais.iloc[0]['Regiao']} com {df_extremos_regionais.iloc[0][f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) pode ser mais propensa a **períodos de frio intenso**.")
            st.markdown(f"**Hipótese:** Regiões com temperaturas mínimas historicamente baixas podem enfrentar **desafios para a agricultura (geadas)** e para a infraestrutura, caso esses valores se tornem ainda mais extremos ou ocorram com maior frequência.")
        elif "Precipitação Total" in nome_var_extremo:
            st.markdown(f"**Observação:** A Região com o maior valor de **{nome_var_extremo}** ( {df_extremos_regionais.iloc[0]['Regiao']} com {df_extremos_regionais.iloc[0][f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) pode estar mais exposta a **chuvas intensas**.")
            st.markdown(f"**Hipótese:** A ocorrência de eventos de precipitação extrema pode indicar uma **maior propensão a inundações, deslizamentos de terra e interrupções em serviços essenciais** em certas regiões, exigindo planejamento urbano e medidas de contenção de riscos.")
        elif "Rajada Máxima de Vento" in nome_var_extremo:
            st.markdown(f"**Observação:** A Região com o maior valor de **{nome_var_extremo}** ( {df_extremos_regionais.iloc[0]['Regiao']} com {df_extremos_regionais.iloc[0][f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) pode experimentar **ventos mais fortes e potencialmente destrutivos**.")
            st.markdown(f"**Hipótese:** Ventos de alta velocidade podem causar **danos à infraestrutura, queda de árvores e interrupção no fornecimento de energia**. Regiões com registros elevados podem necessitar de estruturas mais resilientes e sistemas de alerta para a população.")

    else:
        st.info("Não há dados de extremos disponíveis para a variável e o período selecionados.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
