import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Contrastando o Clima: Padrões de Temperatura e Precipitação entre 2020 e 2024 no Brasil")

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
    
    # Garante que as colunas necessárias existem
    required_cols = ['Temp_Media', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada no arquivo CSV. Verifique seu arquivo.")
            st.stop()

    df = df.dropna(subset=['Mês', 'Ano'] + required_cols)
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia
    if 'Temp_Media' not in df_unificado.columns:
        st.error("Erro Crítico: A coluna 'Temp_Media' não existe e não pôde ser calculada a partir das colunas de máxima e mínima. Verifique o seu arquivo CSV.")
        st.stop()

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Escolha sua Análise:")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    
    # Seleção de Região
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região para Comparação:", regioes)

    st.subheader(f"Comparativo Climático entre 2020 e 2024 na Região {regiao_selecionada}")
    st.markdown("""
    Esta seção vital permite uma análise lado a lado dos padrões de **Temperatura Média** e **Precipitação Total** em **2020** e **2024** para a região escolhida.
    Observe atentamente as diferenças: elas podem revelar a influência de eventos climáticos anuais ou a intensidade da variabilidade climática local.
    """)

    # Filtrar dados para a região selecionada e os anos 2020 e 2024
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]
    
    df_2020 = df_regiao[df_regiao['Ano'] == 2020].groupby('Mês').agg({
        'Temp_Media': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
    }).reindex(range(1, 13)).dropna()

    df_2024 = df_regiao[df_regiao['Ano'] == 2024].groupby('Mês').agg({
        'Temp_Media': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
    }).reindex(range(1, 13)).dropna()
    
    if df_2020.empty or df_2024.empty:
        st.warning(f"Dados incompletos para 2020 ou 2024 na Região {regiao_selecionada}. Não é possível realizar a comparação completa.")
        st.stop()

    col1, col2 = st.columns(2)

    # Mapeamento de números de mês para nomes
    nomes_meses = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    with col1:
        # --- GRÁFICO DE TEMPERATURA MÉDIA ---
        fig_temp, ax_temp = plt.subplots(figsize=(10, 6))
        
        ax_temp.plot(df_2020.index, df_2020['Temp_Media'], marker='o', linestyle='-', color='purple', label='Temperatura Média 2020', linewidth=2)
        ax_temp.plot(df_2024.index, df_2024['Temp_Media'], marker='o', linestyle='--', color='orange', label='Temperatura Média 2024', linewidth=2)
        
        ax_temp.set_title(f'Temperatura Média Mensal - {regiao_selecionada}', fontsize=16, fontweight='bold')
        ax_temp.set_xlabel('Mês', fontsize=12)
        ax_temp.set_ylabel('Temperatura Média (°C)', fontsize=12)
        ax_temp.set_xticks(range(1, 13))
        ax_temp.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)])
        ax_temp.grid(True, linestyle=':', alpha=0.7)
        ax_temp.legend(fontsize=10)
        plt.tight_layout()
        st.pyplot(fig_temp)

    with col2:
        # --- GRÁFICO DE PRECIPITAÇÃO TOTAL ---
        fig_prec, ax_prec = plt.subplots(figsize=(10, 6))
        
        ax_prec.bar(df_2020.index - 0.2, df_2020['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], width=0.4, color='darkgreen', label='Precipitação 2020')
        ax_prec.bar(df_2024.index + 0.2, df_2024['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], width=0.4, color='skyblue', label='Precipitação 2024')
        
        ax_prec.set_title(f'Precipitação Mensal Total - {regiao_selecionada}', fontsize=16, fontweight='bold')
        ax_prec.set_xlabel('Mês', fontsize=12)
        ax_prec.set_ylabel('Precipitação Total (mm)', fontsize=12)
        ax_prec.set_xticks(range(1, 13))
        ax_prec.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)])
        ax_prec.grid(axis='y', linestyle=':', alpha=0.7)
        ax_prec.legend(fontsize=10)
        plt.tight_layout()
        st.pyplot(fig_prec)

    st.markdown("---")

    # --- ANÁLISE PROFUNDA E JUSTIFICATIVA ---
    st.header(f"2020 vs. 2024 na Região {regiao_selecionada}: Eventos Climáticos ou Variabilidade Natural?")
    st.markdown(f"""
    Ao confrontar os padrões climáticos de **2020** e **2024** para a **Região {regiao_selecionada}**, podemos identificar insights cruciais sobre a natureza do clima local. As diferenças observadas nesses gráficos podem ser mais do que simples flutuações anuais; elas podem sinalizar a influência de eventos climáticos específicos ou, alternativamente, a manifestação de uma alta variabilidade intrínseca à região.

    ### Análise da Temperatura Média:
    Observe as linhas de temperatura. Se a linha de **2024** se mantém consistentemente acima (ou abaixo) da de **2020** por vários meses, especialmente em estações-chave, isso pode indicar:
    * **Tendência de Aquecimento/Resfriamento Anual:** Um ano **visivelmente mais quente (ou frio)** que o outro sugere uma possível aceleração de tendências de longo prazo, ou a influência de fenômenos de grande escala (como El Niño/La Niña intensos).
    * **Eventos Extremos de Calor/Frio:** Picos ou vales acentuados em meses específicos de um ano, sem correspondência no outro, podem indicar **ondas de calor ou frio** pontuais, que são eventos climáticos de alto impacto.

    ### Análise da Precipitação Total:
    A comparação das barras de precipitação é igualmente reveladora. Diferenças significativas nos volumes mensais entre os dois anos podem apontar para:
    * **Secas ou Chuvas Intensas:** Um ano com volumes de precipitação drasticamente menores ou maiores que o outro (especialmente durante a estação chuvosa) sugere a ocorrência de **secas prolongadas ou períodos de chuvas torrenciais**. Esses são eventos climáticos extremos com sérias consequências.
    * **Mudança na Sazonalidade:** Se os picos de chuva ocorreram em meses diferentes, ou se a distribuição das chuvas mudou (ex: um ano com chuva mais concentrada, outro mais dispersa), isso aponta para uma **alteração nos padrões sazonais**, uma manifestação de alta variabilidade.

    ### Conclusão: Eventos Climáticos ou Alta Variabilidade?
    * **Eventos Climáticos:** Se você observar diferenças **abruptas e marcantes** em um ou mais meses, ou um padrão de temperaturas ou precipitações consistentemente mais altas/baixas em um ano versus outro, isso **fortemente sugere a influência de um evento climático específico** naquele período. Estes podem ser El Niño/La Niña, bloqueios atmosféricos, ou a passagem de ciclones.
    * **Alta Variabilidade:** Por outro lado, se as diferenças são **menos consistentes**, com um ano sendo mais quente em alguns meses e mais frio em outros, ou com variações de precipitação que não formam um padrão claro de seca/enchente generalizada, isso pode indicar uma **alta variabilidade climática intrínseca à região**. Esta variabilidade exige adaptabilidade contínua por parte dos setores econômicos e da população.

    Ao analisar cuidadosamente os gráficos acima, você pode inferir se a Região {regiao_selecionada} vivenciou anomalias climáticas pontuais em 2020 ou 2024, ou se a sua variabilidade natural foi particularmente acentuada nesses anos.
    """)

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
