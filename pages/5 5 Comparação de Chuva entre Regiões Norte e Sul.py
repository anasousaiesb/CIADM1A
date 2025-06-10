import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Ciclo Hidrológico na Amazônia: Temperatura, Umidade e Precipitação (Região Norte, 2021)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Calcula a Temp_Media se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] + 
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    elif 'Temp_Media' not in df.columns:
        pass # O erro será tratado no bloco principal

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    
    # Garante que as colunas de precipitação e umidade existem
    required_cols = ['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)', 'UMIDADE RELATIVA DO AR, HORARIA (%)']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada no arquivo CSV. Verifique seu arquivo.")
            st.stop()

    df = df.dropna(subset=['Mês', 'Ano'] + required_cols) # Dropar NaNs também das colunas necessárias
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia
    if 'Temp_Media' not in df_unificado.columns:
        st.error("Erro Crítico: A coluna 'Temp_Media' não existe e não pôde ser calculada a partir das colunas de máxima e mínima. Verifique o seu arquivo CSV.")
        st.stop()

    # --- FILTRAGEM PARA A PERGUNTA ESPECÍFICA ---
    regiao_foco = 'Norte'
    ano_foco = 2021
    
    df_norte_2021 = df_unificado[(df_unificado['Regiao'] == regiao_foco) & (df_unificado['Ano'] == ano_foco)].copy()

    if df_norte_2021.empty:
        st.error(f"Não há dados para a Região {regiao_foco} no ano de {ano_foco}. Verifique o seu arquivo CSV.")
        st.stop()

    # Agrupar por mês para obter as médias mensais necessárias
    df_mensal_norte_2021 = df_norte_2021.groupby('Mês').agg({
        'Temp_Media': 'mean',
        'UMIDADE RELATIVA DO AR, HORARIA (%)': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum' # Precipitação é soma, não média
    }).reindex(range(1, 13)).dropna() # Garante todos os meses e remove NaNs
    
    if df_mensal_norte_2021.empty:
        st.info(f"Dados insuficientes para a Região {regiao_foco} em {ano_foco} após agregação mensal.")
        st.stop()

    # Identificar o mês mais chuvoso e mais seco para o ano de 2021 na Região Norte
    mes_chuvoso_default = df_mensal_norte_2021['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].idxmax()
    mes_seco_default = df_mensal_norte_2021['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].idxmin()

    # --- INTERFACE DO USUÁRIO (Controles Interativos) ---
    st.sidebar.header("Selecione os Meses para Comparação:")
    
    # Mapeamento de números de mês para nomes
    nomes_meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    meses_disponiveis = sorted(df_mensal_norte_2021.index.tolist())
    
    mes_chuvoso_selecionado = st.sidebar.selectbox(
        "Escolha o Mês 'Chuvoso' para Análise:",
        options=meses_disponiveis,
        format_func=lambda x: nomes_meses.get(x, str(x)),
        index=meses_disponiveis.index(mes_chuvoso_default) if mes_chuvoso_default in meses_disponiveis else 0
    )
    
    mes_seco_selecionado = st.sidebar.selectbox(
        "Escolha o Mês 'Seco' para Análise:",
        options=meses_disponiveis,
        format_func=lambda x: nomes_meses.get(x, str(x)),
        index=meses_disponiveis.index(mes_seco_default) if mes_seco_default in meses_disponiveis else 0
    )

    # --- VISUALIZAÇÃO INTERATIVA ---
    st.subheader(f"Comportamento Mensal de Temperatura e Umidade na Região {regiao_foco} em {ano_foco}")
    st.markdown(f"""
    Explore a relação entre **temperatura média** e **umidade relativa do ar** ao longo de 2021 na Região Norte.
    Observe como o **mês chuvoso ({nomes_meses[mes_chuvoso_selecionado]})** e o **mês seco ({nomes_meses[mes_seco_selecionado]})** selecionados se destacam nos padrões do ciclo hidrológico.
    """)

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Eixo Y1: Temperatura Média
    color = 'tab:red'
    ax1.set_xlabel('Mês')
    ax1.set_ylabel('Temperatura Média (°C)', color=color)
    ax1.plot(df_mensal_norte_2021.index, df_mensal_norte_2021['Temp_Media'], color=color, marker='o', linestyle='-', label='Temperatura Média')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)], rotation=45, ha='right')
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Eixo Y2: Umidade Relativa do Ar
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Umidade Relativa do Ar (%)', color=color)
    ax2.plot(df_mensal_norte_2021.index, df_mensal_norte_2021['UMIDADE RELATIVA DO AR, HORARIA (%)'], color=color, marker='x', linestyle='--', label='Umidade Relativa')
    ax2.tick_params(axis='y', labelcolor=color)

    # Destaque para os meses selecionados
    # Mês Chuvoso
    temp_chuvoso = df_mensal_norte_2021.loc[mes_chuvoso_selecionado, 'Temp_Media']
    umid_chuvoso = df_mensal_norte_2021.loc[mes_chuvoso_selecionado, 'UMIDADE RELATIVA DO AR, HORARIA (%)']
    prec_chuvoso = df_mensal_norte_2021.loc[mes_chuvoso_selecionado, 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']
    ax1.plot(mes_chuvoso_selecionado, temp_chuvoso, 's', color='red', markersize=10, label=f'{nomes_meses[mes_chuvoso_selecionado]} (Chuvoso)')
    ax2.plot(mes_chuvoso_selecionado, umid_chuvoso, 's', color='blue', markersize=10)
    
    # Mês Seco
    temp_seco = df_mensal_norte_2021.loc[mes_seco_selecionado, 'Temp_Media']
    umid_seco = df_mensal_norte_2021.loc[mes_seco_selecionado, 'UMIDADE RELATIVA DO AR, HORARIA (%)']
    prec_seco = df_mensal_norte_2021.loc[mes_seco_selecionado, 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']
    ax1.plot(mes_seco_selecionado, temp_seco, 'd', color='darkred', markersize=10, label=f'{nomes_meses[mes_seco_selecionado]} (Seco)')
    ax2.plot(mes_seco_selecionado, umid_seco, 'd', color='darkblue', markersize=10)

    # Adicionar uma legenda combinada
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left', bbox_to_anchor=(1.1, 1), title='Legenda')


    fig.tight_layout(rect=[0, 0, 0.9, 1]) # Ajusta para acomodar a legenda
    st.pyplot(fig)

    st.markdown("---")

    # --- ANÁLISE E JUSTIFICATIVA DO CICLO HIDROLÓGICO ---
    st.header("Análise Detalhada: Temperatura, Umidade e o Ciclo Hidrológico da Amazônia")
    st.markdown(f"""
    Ao observar o comportamento da **Temperatura Média** e da **Umidade Relativa do Ar** na Região Norte durante 2021, especialmente nos meses de **{nomes_meses[mes_chuvoso_selecionado]}** (mês chuvoso selecionado) e **{nomes_meses[mes_seco_selecionado]}** (mês seco selecionado), podemos discernir os padrões cruciais do ciclo hidrológico amazônico:

    **No Mês Chuvoso ({nomes_meses[mes_chuvoso_selecionado]}, Precipitação: {prec_chuvoso:.2f} mm):**
    * **Temperatura:** A temperatura média tende a ser **ligeiramente mais baixa ou estável** ({temp_chuvoso:.2f}°C) em comparação com o mês seco, devido à maior cobertura de nuvens e à energia absorvida pela evaporação da água. As chuvas frequentes ajudam a mitigar o aquecimento excessivo.
    * **Umidade:** A **umidade relativa do ar atinge seus níveis mais altos** ({umid_chuvoso:.2f}%), refletindo a intensa evapotranspiração da floresta e a abundante disponibilidade de água na atmosfera, que resulta em chuvas. Este é o período de maior atividade do ciclo hidrológico.

    **No Mês Seco ({nomes_meses[mes_seco_selecionado]}, Precipitação: {prec_seco:.2f} mm):**
    * **Temperatura:** A temperatura média geralmente é **mais elevada** ({temp_seco:.2f}°C) e pode apresentar maiores variações diárias, pois há menos cobertura de nuvens para bloquear a radiação solar.
    * **Umidade:** A **umidade relativa do ar é significativamente menor** ({umid_seco:.2f}%), indicando uma redução na disponibilidade de água e uma menor taxa de evapotranspiração. Embora ainda haja alguma chuva, o volume é muito reduzido em comparação com a estação chuvosa.

    **Ilustrando o Ciclo Hidrológico da Amazônia:**

    O gráfico demonstra claramente a interconexão entre estas variáveis. Durante a estação chuvosa, a **alta umidade** e a **precipitação abundante** são impulsionadas pela evapotranspiração da vasta floresta e pela atuação de sistemas como a Zona de Convergência Intertropical (ZCIT). A temperatura se mantém relativamente estável devido ao efeito de resfriamento das chuvas.

    Já na estação menos chuvosa (popularmente chamada de "seca" na Amazônia, mas ainda com alguma chuva), a **radiação solar pode ser mais intensa**, resultando em temperaturas ligeiramente mais altas e uma **queda notável na umidade**, pois a disponibilidade de água para evapotranspiração diminui, reduzindo a formação de nuvens e, consequentemente, a precipitação.

    Essa dinâmica é vital para a saúde da floresta e para o regime hídrico de grande parte do Brasil, mostrando como as condições atmosféricas variam drasticamente entre os períodos de chuva e de menor chuva, influenciando diretamente o ecossistema e as atividades humanas na região.
    """)

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
