import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Padrões Diários de Temperatura e Umidade por Estação (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Converte colunas para numérico, tratando erros
    cols_to_numeric = [
        'Ano', 'Mês', 'Hora UTC',
        'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)',
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'UMIDADE RELATIVA DO AR, HORARIA (%)'
    ]
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Preencher 'Temp_Media' se não existir
    if 'Temp_Media' not in df.columns and \
       'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    elif 'Temp_Media' not in df.columns and 'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)' in df.columns:
        df['Temp_Media'] = df['TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)'] # Usar bulbo seco como proxy se não tiver max/min hora ant.
    elif 'Temp_Media' not in df.columns:
        st.warning("Não foi possível calcular a 'Temp_Media' a partir das colunas disponíveis. A análise de temperatura pode ser limitada.")

    df = df.dropna(subset=['Ano', 'Mês', 'Hora UTC', 'Temp_Media', 'UMIDADE RELATIVA DO AR, HORARIA (%)'])
    
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se as colunas essenciais para a análise existem
    if 'Temp_Media' not in df_unificado.columns or \
       'UMIDADE RELATIVA DO AR, HORARIA (%)' not in df_unificado.columns or \
       'Hora UTC' not in df_unificado.columns:
        st.error("Erro: Colunas essenciais (Temp_Media, UMIDADE RELATIVA DO AR, HORARIA (%), Hora UTC) não encontradas ou não puderam ser calculadas. Verifique seu arquivo CSV.")
        st.stop()

    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("---")
    st.header("Explorando a Dinâmica Diária de Temperatura e Umidade")
    st.markdown("""
        Esta aplicação analisa como a **temperatura** (média diária) e a **umidade relativa**
        variam ao longo das 24 horas do dia, em diferentes **estações do ano**, para uma região selecionada.
        Compreender esses padrões é fundamental para diversas áreas, como saúde, agricultura e consumo de energia.
        """)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Análise")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", regioes)

    # Mapeamento de Meses para Estações no Brasil (simplificado para fins de exemplo)
    # Note: As estações variam um pouco por região, mas vamos usar um padrão geral.
    estacoes = {
        'Verão (Dez-Fev)': [12, 1, 2],
        'Outono (Mar-Mai)': [3, 4, 5],
        'Inverno (Jun-Ago)': [6, 7, 8],
        'Primavera (Set-Nov)': [9, 10, 11]
    }
    nome_estacao_selecionada = st.sidebar.selectbox("Selecione a Estação do Ano:", list(estacoes.keys()))
    meses_estacao = estacoes[nome_estacao_selecionada]

    st.markdown("---")

    # --- PERGUNTA CENTRAL DA ANÁLISE ---
    st.subheader(f"Como a temperatura e a umidade variam ao longo do dia na Região {regiao_selecionada} durante o {nome_estacao_selecionada}?")
    st.markdown("""
        Esta seção apresenta gráficos que detalham o ciclo diário da temperatura média e da umidade relativa
        para a região e estação selecionadas. Isso nos ajuda a identificar as horas mais quentes, mais frias,
        mais úmidas e mais secas do dia.
        """)
    
    df_regiao_estacao = df_unificado[
        (df_unificado['Regiao'] == regiao_selecionada) &
        (df_unificado['Mês'].isin(meses_estacao))
    ]

    if df_regiao_estacao.empty:
        st.warning(f"Não foram encontrados dados para a Região {regiao_selecionada} durante o {nome_estacao_selecionada}.")
    else:
        # Agrupamento por hora do dia
        df_ciclo_diario = df_regiao_estacao.groupby('Hora UTC').agg(
            Temp_Media_Diaria=('Temp_Media', 'mean'),
            Umidade_Media_Diaria=('UMIDADE RELATIVA DO AR, HORARIA (%)', 'mean'),
            Temp_Max_Diaria=('TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)', 'mean'), # Usar se disponível
            Temp_Min_Diaria=('TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)', 'mean')  # Usar se disponível
        ).reindex(range(0, 24)).reset_index()

        # --- GRÁFICO 1: CICLO DIÁRIO DE TEMPERATURA ---
        st.subheader(f"1. Ciclo Diário da Temperatura Média (°C) - {regiao_selecionada}, {nome_estacao_selecionada}")
        st.markdown("""
            Este gráfico de linha mostra o comportamento típico da temperatura média ao longo das 24 horas do dia.
            
            **Propósito:** Identificar os horários de pico de calor e de frio, e a amplitude térmica diária média.
            
            **Interpretação:** Geralmente, as temperaturas mais baixas ocorrem nas primeiras horas da manhã,
            e as mais altas no meio ou fim da tarde. A forma da curva pode indicar a presença de ilhas de calor
            ou outros fenômenos locais.
            """)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df_ciclo_diario['Hora UTC'], df_ciclo_diario['Temp_Media_Diaria'], marker='o', linestyle='-', color='red', label='Temperatura Média')
        
        if 'Temp_Max_Diaria' in df_ciclo_diario.columns and 'Temp_Min_Diaria' in df_ciclo_diario.columns:
             # Plotar máximas e mínimas horárias se existirem e não forem NaN
            if not df_ciclo_diario['Temp_Max_Diaria'].isnull().all():
                ax.plot(df_ciclo_diario['Hora UTC'], df_ciclo_diario['Temp_Max_Diaria'], linestyle='--', color='lightcoral', alpha=0.7, label='Média das Máximas Horárias')
            if not df_ciclo_diario['Temp_Min_Diaria'].isnull().all():
                ax.plot(df_ciclo_diario['Hora UTC'], df_ciclo_diario['Temp_Min_Diaria'], linestyle='--', color='skyblue', alpha=0.7, label='Média das Mínimas Horárias')


        ax.set_xlabel('Hora do Dia (UTC)', fontsize=12)
        ax.set_ylabel('Temperatura Média (°C)', fontsize=12)
        ax.set_title(f'Ciclo Diário da Temperatura - {regiao_selecionada}, {nome_estacao_selecionada}', fontsize=16)
        ax.set_xticks(range(0, 24, 2))
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")

        # --- GRÁFICO 2: CICLO DIÁRIO DE UMIDADE RELATIVA ---
        st.subheader(f"2. Ciclo Diário da Umidade Relativa (%) - {regiao_selecionada}, {nome_estacao_selecionada}")
        st.markdown("""
            Este gráfico de linha mostra o comportamento típico da umidade relativa do ar ao longo das 24 horas do dia.
            
            **Propósito:** Visualizar os horários de maior e menor umidade.
            
            **Interpretação:** A umidade relativa geralmente é mais alta nas primeiras horas da manhã (associada ao frio e ponto de orvalho)
            e mais baixa no período da tarde, quando a temperatura está mais elevada. Variações nesse padrão podem indicar
            influência de massas de ar, ventos ou outros fatores.
            """)
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(df_ciclo_diario['Hora UTC'], df_ciclo_diario['Umidade_Media_Diaria'], marker='o', linestyle='-', color='blue', label='Umidade Relativa Média')
        
        ax2.set_xlabel('Hora do Dia (UTC)', fontsize=12)
        ax2.set_ylabel('Umidade Relativa do Ar (%)', fontsize=12)
        ax2.set_title(f'Ciclo Diário da Umidade Relativa - {regiao_selecionada}, {nome_estacao_selecionada}', fontsize=16)
        ax2.set_xticks(range(0, 24, 2))
        ax2.grid(True, linestyle='--', alpha=0.6)
        ax2.legend()
        plt.tight_layout()
        st.pyplot(fig2)

        st.markdown("---")

        # --- GRÁFICO 3: RELAÇÃO TEMPERATURA vs UMIDADE (scatter plot) ---
        st.subheader(f"3. Relação entre Temperatura e Umidade Média por Hora")
        st.markdown("""
            Este gráfico de dispersão (scatter plot) explora a relação entre a temperatura média horária
            e a umidade relativa média horária na região e estação selecionadas.
            
            **Propósito:** Visualizar se há uma correlação clara entre temperatura e umidade ao longo do ciclo diário.
            
            **Interpretação:** Frequentemente, observa-se uma correlação inversa: temperaturas mais altas
            tendem a estar associadas a umidade mais baixa, e vice-versa. Desvios desse padrão (pontos isolados)
            podem indicar condições climáticas atípicas para a hora ou estação.
            """)
        
        fig3, ax3 = plt.subplots(figsize=(10, 8))
        scatter = ax3.scatter(
            df_ciclo_diario['Temp_Media_Diaria'],
            df_ciclo_diario['Umidade_Media_Diaria'],
            c=df_ciclo_diario['Hora UTC'], # Colore os pontos pela hora do dia
            cmap='plasma', # Mapa de cores para a hora
            s=100, # Tamanho dos pontos
            alpha=0.8
        )
        
        ax3.set_xlabel('Temperatura Média (°C)', fontsize=12)
        ax3.set_ylabel('Umidade Relativa Média (%)', fontsize=12)
        ax3.set_title(f'Temperatura vs. Umidade Relativa por Hora - {regiao_selecionada}, {nome_estacao_selecionada}', fontsize=16)
        ax3.grid(True, linestyle='--', alpha=0.6)
        
        # Adiciona a barra de cores (legend)
        cbar = fig3.colorbar(scatter, ax=ax3)
        cbar.set_label('Hora do Dia (UTC)', fontsize=10)

        # Adicionar rótulos para algumas horas chave (ex: 0h, 6h, 12h, 18h)
        for _, row in df_ciclo_diario[df_ciclo_diario['Hora UTC'].isin([0, 6, 12, 18])].iterrows():
            ax3.text(row['Temp_Media_Diaria'], row['Umidade_Media_Diaria'],
                     f"{int(row['Hora UTC'])}h", fontsize=9, ha='right', va='bottom',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))

        plt.tight_layout()
        st.pyplot(fig3)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada ou não pôde ser processada. Verifique se o seu arquivo contém os dados necessários e se os nomes das colunas estão corretos.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
