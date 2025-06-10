import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- INITIAL CONFIGURATIONS ---
st.set_page_config(layout="wide")
st.title("Análise de Extremos de Temperatura e Ponto de Orvalho por Estação (2020-2025)")

# Relative path to the unified CSV file
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNCTION TO LOAD AND PREPARE DATA ---
@st.cache_data
def carregar_dados(caminho):
    """Loads and processes the climate data file."""
    df = pd.read_csv(caminho)

    # Columns to convert to numeric, handling errors
    cols_to_numeric = [
        'Ano', 'Mês', 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA DO PONTO DE ORVALHO (°C)'
    ]
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with NaN in essential columns
    df = df.dropna(subset=[
        'Ano', 'Mês', 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA DO PONTO DE ORVALHO (°C)'
    ])

    return df

# --- DATA LOADING AND ERROR HANDLING ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # Check for essential columns
    required_cols = [
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA DO PONTO DE ORVALHO (°C)'
    ]
    for col in required_cols:
        if col not in df_unificado.columns:
            st.error(f"Critical Error: Column '{col}' not found in the CSV file. Please check your CSV.")
            st.stop()

    # --- APP INITIAL EXPLANATION ---
    st.markdown("---")
    st.header("Análise de Extremos de Temperatura e Ponto de Orvalho")
    st.markdown("""
        Esta aplicação explora como as **temperaturas extremas** (máxima e mínima) e a
        **temperatura do ponto de orvalho** variam entre as regiões do Brasil durante os
        meses mais quentes e mais frios do ano (considerando a média do período 2020-2025).
        Compreender essas variações é vital para avaliar o potencial de estresse térmico,
        condições de geada e conforto ambiental.
        """)

    # --- USER INTERFACE ---
    st.sidebar.header("Filtros de Análise")

    # Determine the warmest and coldest months based on overall data average
    avg_temp_by_month = df_unificado.groupby('Mês')['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'].mean()
    warmest_month_num = avg_temp_by_month.idxmax()
    coldest_month_num = avg_temp_by_month.idxmin()

    meses_nome = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    warmest_month_name = meses_nome[warmest_month_num]
    coldest_month_name = meses_nome[coldest_month_num]

    periodo_selecionado = st.sidebar.radio(
        "Selecione o Período de Análise:",
        (f"Mês Mais Quente ({warmest_month_name})", f"Mês Mais Frio ({coldest_month_name})")
    )

    selected_month_num = warmest_month_num if "Mês Mais Quente" in periodo_selecionado else coldest_month_num
    selected_month_name = warmest_month_name if "Mês Mais Quente" in periodo_selecionado else coldest_month_name

    st.markdown("---")

    # --- CENTRAL QUESTION ---
    st.subheader(f"Como os extremos de temperatura e o ponto de orvalho variam por região durante o {selected_month_name}?")
    st.markdown("""
        Esta seção compara as temperaturas máximas e mínimas, e a temperatura do ponto de orvalho
        entre as diferentes regiões do Brasil para o mês selecionado.
        """)

    # Filter data for the selected month across all regions
    df_periodo = df_unificado[df_unificado['Mês'] == selected_month_num]

    if df_periodo.empty:
        st.warning(f"No data found for {selected_month_name}.")
    else:
        # Calculate regional averages for the selected month
        df_analise_regional = df_periodo.groupby('Regiao').agg(
            Temp_Maxima_Media=('TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)', 'mean'),
            Temp_Minima_Media=('TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)', 'mean'),
            Ponto_Orvalho_Media=('TEMPERATURA DO PONTO DE ORVALHO (°C)', 'mean')
        ).reset_index()

        # Sort for better visualization
        df_analise_regional = df_analise_regional.sort_values(by='Temp_Maxima_Media', ascending=False)

        # --- GRAPH 1: REGIONAL TEMPERATURE EXTREMES ---
        st.subheader(f"1. Temperaturas Máxima e Mínima Média por Região - {selected_month_name}")
        st.markdown("""
            Este gráfico de barras duplas compara a **temperatura máxima média** e a
            **temperatura mínima média** para cada região do Brasil durante o mês selecionado.
            
            **Propósito:** Visualizar as regiões mais quentes e mais frias, e a amplitude térmica
            média entre elas no período.
            
            **Interpretação:** Regiões com barras azuis (máxima) mais altas e barras laranjas (mínima)
            também mais altas são mais quentes. A diferença entre as barras azul e laranja indica a
            amplitude térmica diária média.
            """)

        fig, ax = plt.subplots(figsize=(12, 7))
        bar_width = 0.35
        index = np.arange(len(df_analise_regional['Regiao']))

        bars1 = ax.bar(index - bar_width/2, df_analise_regional['Temp_Maxima_Media'], bar_width, label='Temp. Máxima Média (°C)', color='orangered')
        bars2 = ax.bar(index + bar_width/2, df_analise_regional['Temp_Minima_Media'], bar_width, label='Temp. Mínima Média (°C)', color='skyblue')

        ax.set_xlabel('Região', fontsize=12)
        ax.set_ylabel('Temperatura Média (°C)', fontsize=12)
        ax.set_title(f'Temperaturas Média Máxima e Média Mínima por Região - {selected_month_name}', fontsize=16)
        ax.set_xticks(index)
        ax.set_xticklabels(df_analise_regional['Regiao'], rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")

        # --- GRAPH 2: REGIONAL DEW POINT TEMPERATURE ---
        st.subheader(f"2. Temperatura do Ponto de Orvalho Média por Região - {selected_month_name}")
        st.markdown("""
            Este gráfico de barras exibe a **temperatura média do ponto de orvalho** para cada região
            do Brasil durante o mês selecionado.
            
            **Propósito:** Avaliar a umidade absoluta do ar e o potencial para sensações de "ar abafado"
            (ponto de orvalho alto) ou "ar seco" (ponto de orvalho baixo), além do risco de formação de geada
            em certas condições (ponto de orvalho próximo ou abaixo de zero).
            
            **Interpretação:**
            * **Ponto de Orvalho Alto (ex: > 20°C):** Indica muito vapor de água no ar, associado a calor
                e sensação de abafamento, comum em regiões tropicais úmidas. Potencial de calor estressante.
            * **Ponto de Orvalho Baixo (ex: < 10°C):** Indica ar seco.
            * **Ponto de Orvalho Próximo ou Abaixo de 0°C:** Em combinação com temperaturas do ar próximas a 0°C,
                aumenta o risco de geada.
            """)
        
        df_analise_regional_dew = df_analise_regional.sort_values(by='Ponto_Orvalho_Media', ascending=False)

        fig2, ax2 = plt.subplots(figsize=(12, 7))
        bars_dew = ax2.bar(df_analise_regional_dew['Regiao'], df_analise_regional_dew['Ponto_Orvalho_Media'], color='forestgreen')

        ax2.set_xlabel('Região', fontsize=12)
        ax2.set_ylabel('Temperatura do Ponto de Orvalho Média (°C)', fontsize=12)
        ax2.set_title(f'Temperatura Média do Ponto de Orvalho por Região - {selected_month_name}', fontsize=16)
        ax2.tick_params(axis='x', rotation=45, ha='right')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        # Add values on top of bars
        for bar in bars_dew:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                     f'{height:.1f}', ha='center', va='bottom', fontsize=9, color='black')

        plt.tight_layout()
        st.pyplot(fig2)

except FileNotFoundError:
    st.error(f"Error: The file '{caminho_arquivo_unificado}' was not found. Please check the path and file location.")
except KeyError as e:
    st.error(f"Error: Column '{e}' not found or could not be processed. Please verify your CSV file contains the necessary data and column names are correct.")
except Exception as e:
    st.error(f"An unexpected error occurred during execution: {e}")
