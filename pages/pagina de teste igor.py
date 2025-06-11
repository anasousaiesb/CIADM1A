import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Detecção de Dias Climáticos Atípicos (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos, calculando médias/somas diárias."""
    df = pd.read_csv(caminho)

    # --- Renomear colunas para facilitar o uso no código (opcional, mas boa prática) ---
    # Mapeamento dos nomes de coluna do seu CSV para nomes padronizados no código
    # **REVISADO COM BASE NO ERRO E VARIÁVEIS FORNECIDAS**
    col_mapping = {
        'Hora UTC': 'Hora_UTC',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'Precipitacao_Total_Horaria',
        'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)': 'Pressao_Atmosferica_Horaria', # Keep if exists
        'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)': 'Pressao_Maxima_Hora_Ant',      # Keep if exists
        'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)': 'Pressao_Minima_Hora_Ant',      # Keep if exists
        'RADIACAO GLOBAL (Kj/m²)': 'Radiacao_Global_Horaria',
        
        # **Atenção aqui:** Se "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)" NÃO existe,
        # você precisa usar uma coluna de temperatura que exista.
        # Baseado no seu prompt inicial, as temperaturas disponíveis são MÁXIMA e MÍNIMA.
        # Vamos usar a média delas como uma proxy para a temperatura horária.
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': 'Temperatura_Maxima_Hora_Ant',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': 'Temperatura_Minima_Hora_Ant',
        
        # **Atenção aqui:** Se "UMIDADE RELATIVA DO AR, HORARIA (%)" NÃO existe no seu CSV,
        # você PRECISA identificar a coluna de umidade correta ou remover a umidade da análise.
        # Por enquanto, vou manter o nome esperado, mas se o erro persistir,
        # o nome real da coluna de umidade no seu CSV é o problema.
        'UMIDADE RELATIVA DO AR, HORARIA (%)': 'Umidade_Relativa_Horaria',
        
        'VENTO, RAJADA MAXIMA (m/s)': 'Vento_Rajada_Maxima',        # Keep if exists
        'VENTO, VELOCIDADE HORARIA (m/s)': 'Vento_Velocidade_Horaria', # Keep if exists
        
        'Regiao': 'Regiao',
        'Mês': 'Mês',
        'Ano': 'Ano'
    }
    
    # Aplica o mapeamento, ignorando chaves que não existem no DF
    df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})

    # --- Criação da coluna 'Data_Original' ---
    # Se 'Data' não existe, precisamos criá-la a partir de 'Ano' e 'Mês'.
    # Para permitir o agrupamento diário, vamos assumir o dia 1 do mês.
    # **NOTA:** Se seus dados são de fato horários e vêm de um arquivo que
    # tem uma coluna de data/hora completa, use essa coluna diretamente
    # e ajuste o mapeamento.
    
    # Ensure 'Ano' and 'Mês' are available to construct a date
    if 'Ano' not in df.columns or 'Mês' not in df.columns:
        st.error("Erro Crítico: Colunas 'Ano' ou 'Mês' não encontradas para construir a data. Verifique os nomes das colunas em seu CSV.")
        st.stop()
    
    # Creating a dummy 'Day' column for daily aggregation if not explicitly present, defaulting to 1
    # This is important for .replace(hour=...) to work correctly later, assuming a full date is needed
    if 'Dia' not in df.columns: # Assuming 'Dia' is not explicitly mapped or renamed
        df['Dia'] = 1 # Default to the first day of the month for all entries

    # Construct Data_Original from Ano, Mês, and the (potentially dummy) Dia
    df['Data_Original'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mês'].astype(str) + '-' + df['Dia'].astype(str), errors='coerce')

    # Now, combine 'Data_Original' and 'Hora_UTC' into a single complete timestamp
    if 'Hora_UTC' in df.columns:
        df['Hora_UTC'] = pd.to_numeric(df['Hora_UTC'], errors='coerce').fillna(0).astype(int)
        df['Data_Hora_Completa'] = df.apply(lambda row: row['Data_Original'].replace(hour=row['Hora_UTC']) if pd.notna(row['Data_Original']) else pd.NaT, axis=1)
    else:
        st.warning("Coluna 'Hora UTC' não encontrada. A análise diária será baseada apenas na data, não na hora exata.")
        df['Data_Hora_Completa'] = df['Data_Original']

    # --- Cálculo da Temperatura Horária Média a partir de Máx/Min ---
    # Se 'Temperatura_Bulbo_Seco_Horaria' não existe, criamos uma proxy.
    if 'Temperatura_Maxima_Hora_Ant' in df.columns and 'Temperatura_Minima_Hora_Ant' in df.columns:
        df['Temperatura_Bulbo_Seco_Horaria'] = (df['Temperatura_Maxima_Hora_Ant'] + df['Temperatura_Minima_Hora_Ant']) / 2
    else:
        st.error("Erro: Colunas 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' ou 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' não encontradas para calcular a temperatura horária. Verifique seu CSV.")
        st.stop()

    # Verificar se a coluna de umidade existe após o mapeamento
    if 'Umidade_Relativa_Horaria' not in df.columns:
        st.error("Erro: Coluna 'UMIDADE RELATIVA DO AR, HORARIA (%)' não encontrada. Por favor, verifique o nome exato da coluna de umidade no seu arquivo CSV.")
        st.stop()
    
    # Remover linhas com NaN em colunas críticas após conversão
    df = df.dropna(subset=[
        'Data_Hora_Completa', 'Regiao', 'Mês', 'Ano',
        'Temperatura_Bulbo_Seco_Horaria', # Agora garantimos que ela existe
        'Umidade_Relativa_Horaria',     # Agora garantimos que ela existe
        'Radiacao_Global_Horaria'
    ])

    # Agrupar por dia, região, mês, ano para obter valores diários
    df_diario = df.groupby(['Data_Original', 'Regiao', 'Mês', 'Ano']).agg(
        Temp_Media_Diaria=('Temperatura_Bulbo_Seco_Horaria', 'mean'),
        Umidade_Media_Diaria=('Umidade_Relativa_Horaria', 'mean'),
        Radiacao_Total_Diaria=('Radiacao_Global_Horaria', 'sum')
    ).reset_index()

    return df_diario

# --- O restante do código (calcular_score_atipicidade e o bloco try/except) permanece o mesmo ---
# --- CÁLCULO DO SCORE DE ATIPICIDADE ---
def calcular_score_atipicidade(df_diario_regiao):
    """
    Calculates an atypicality score for each day, based on the standard deviations
    of variables relative to the historical monthly average for that region.
    """
    df_scores = df_diario_regiao.copy()
    
    # Calculate historical monthly averages and standard deviations for each variable
    historico_mensal = df_scores.groupby(['Mês']).agg(
        Temp_Media_Mensal=('Temp_Media_Diaria', 'mean'),
        Temp_Std_Mensal=('Temp_Media_Diaria', 'std'),
        Umidade_Media_Mensal=('Umidade_Media_Diaria', 'mean'),
        Umidade_Std_Mensal=('Umidade_Media_Diaria', 'std'),
        Radiacao_Media_Mensal=('Radiacao_Total_Diaria', 'mean'),
        Radiacao_Std_Mensal=('Radiacao_Total_Diaria', 'std')
    )
    
    # Merge with daily data for Z-score calculation
    df_scores = df_scores.merge(historico_mensal, on='Mês', how='left')

    # Calculate Z-scores (number of standard deviations from the mean)
    # Add a small value to avoid division by zero if std is 0
    epsilon = 1e-6 
    df_scores['Z_Temp'] = (df_scores['Temp_Media_Diaria'] - df_scores['Temp_Media_Mensal']) / (df_scores['Temp_Std_Mensal'] + epsilon)
    df_scores['Z_Umidade'] = (df_scores['Umidade_Media_Diaria'] - df_scores['Umidade_Media_Mensal']) / (df_scores['Umidade_Std_Mensal'] + epsilon)
    df_scores['Z_Radiacao'] = (df_scores['Radiacao_Total_Diaria'] - df_scores['Radiacao_Media_Mensal']) / (df_scores['Radiacao_Std_Mensal'] + epsilon)

    # Calculate a combined atypicality score (magnitude of the deviation)
    # We use the absolute value of the Z-score and sum them
    df_scores['Score_Atipicidade'] = df_scores['Z_Temp'].abs() + df_scores['Z_Umidade'].abs() + df_scores['Z_Radiacao'].abs()
    
    # Handle NaNs resulting from std=0 or missing data (if applicable)
    df_scores['Score_Atipicidade'] = df_scores['Score_Atipicidade'].fillna(0) # Treat days where score calculation failed, maybe due to insufficient data for std

    return df_scores.sort_values(by='Score_Atipicidade', ascending=False)


# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_diario_unificado = carregar_dados(caminho_arquivo_unificado)
    
    if df_diario_unificado.empty:
        st.error("Não foi possível carregar ou processar os dados diários. Verifique seu arquivo CSV e as colunas.")
        st.stop()

    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("---")
    st.header("Identificação de Dias Climáticos Atípicos (2020-2025)")
    st.markdown("""
        Esta aplicação busca responder: **"Quais dias apresentaram condições climáticas mais 'incomuns'
        ou 'fora do padrão' em uma dada região, considerando simultaneamente temperatura, umidade e radiação global?"**
        
        Um dia é considerado "incomum" se seus valores médios de temperatura e umidade,
        e o total de radiação, se desviam significativamente da média histórica para o mês
        e região específicos. Isso é calculado usando um "score de atipicidade" baseado
        no número de desvios padrão da média mensal.
        """)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Análise")
    
    regioes = sorted(df_diario_unificado['Regiao'].unique())
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", regioes)

    num_dias_atipicos = st.sidebar.slider(
        "Número de Dias Atípicos para Exibir:",
        min_value=5, max_value=50, value=10, step=5,
        help="Quantos dos dias mais incomuns você deseja visualizar."
    )
    
    st.markdown("---")

    # --- PERGUNTA CENTRAL DA ANÁLISE ---
    st.subheader(f"Dias Climáticos Mais Atípicos na Região {regiao_selecionada}")
    st.markdown("""
        Esta seção apresenta os dias que mais se destacaram em termos de atipicidade,
        com base nos desvios simultâneos de temperatura, umidade e radiação global
        em relação às médias mensais históricas da região.
        """)
    
    df_regiao = df_diario_unificado[df_diario_unificado['Regiao'] == regiao_selecionada]

    if df_regiao.empty:
        st.warning(f"Não foram encontrados dados para a Região {regiao_selecionada}.")
    else:
        df_dias_atipicos = calcular_score_atipicidade(df_regiao)

        if df_dias_atipicos.empty or df_dias_atipicos['Score_Atipicidade'].sum() == 0:
            st.info(f"Não foi possível calcular scores de atipicidade para a região {regiao_selecionada} (dados insuficientes ou sem variância).")
        else:
            top_dias_atipicos = df_dias_atipicos.head(num_dias_atipicos)

            st.write(f"Os **{num_dias_atipicos} dias mais atípicos** na região **{regiao_selecionada}** foram:")
            
            # Format for display
            top_dias_display = top_dias_atipicos[[
                'Data_Original', 'Score_Atipicidade', 'Temp_Media_Diaria',
                'Umidade_Media_Diaria', 'Radiacao_Total_Diaria',
                'Z_Temp', 'Z_Umidade', 'Z_Radiacao'
            ]].copy()
            top_dias_display['Data_Original'] = top_dias_display['Data_Original'].dt.strftime('%d/%m/%Y')
            top_dias_display = top_dias_display.rename(columns={
                'Data_Original': 'Data',
                'Score_Atipicidade': 'Score Atipicidade',
                'Temp_Media_Diaria': 'Temp. Média (°C)',
                'Umidade_Media_Diaria': 'Umid. Média (%)',
                'Radiacao_Total_Diaria': 'Rad. Total (Kj/m²)',
                'Z_Temp': 'Z-Score Temp',
                'Z_Umidade': 'Z-Score Umid.',
                'Z_Radiacao': 'Z-Score Rad.'
            })
            st.dataframe(top_dias_display.set_index('Data').style.format({
                'Score Atipicidade': "{:.2f}",
                'Temp. Média (°C)': "{:.1f}",
                'Umid. Média (%)': "{:.1f}",
                'Rad. Total (Kj/m²)': "{:.0f}",
                'Z-Score Temp': "{:.2f}",
                'Z-Score Umid.': "{:.2f}",
                'Z-Score Rad.': "{:.2f}"
            }))

            st.markdown("---")

            # --- GRÁFICO: DISTRIBUIÇÃO DOS SCORES DE ATIPICIDADE ---
            st.subheader(f"Distribuição dos Scores de Atipicidade - Região {regiao_selecionada}")
            st.markdown("""
                Este histograma mostra a distribuição dos scores de atipicidade para todos os dias
                na região selecionada. A maioria dos dias tende a ter scores baixos (próximos da média),
                enquanto os "dias incomuns" são representados pelas barras mais à direita do gráfico.
                
                **Propósito:** Visualizar quão frequentemente a região experimenta dias "normais" versus "atípicos".
                
                **Interpretação:** Uma cauda longa para a direita indica que a região tem alguns dias
                muito incomuns. Isso pode ser útil para entender a variabilidade climática extrema
                da região.
                """)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df_dias_atipicos['Score_Atipicidade'], bins=30, color='darkcyan', edgecolor='black')
            ax.set_xlabel('Score de Atipicidade', fontsize=12)
            ax.set_ylabel('Número de Dias', fontsize=12)
            ax.set_title(f'Distribuição dos Scores de Atipicidade - Região {regiao_selecionada}', fontsize=16)
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            plt.tight_layout()
            st.pyplot(fig)

            st.markdown("---")

            # --- GRÁFICO 2: DETALHES DO DIA MAIS ATÍPICO ---
            if not top_dias_atipicos.empty:
                dia_mais_atipico = top_dias_atipicos.iloc[0]
                mes_do_dia_mais_atipico = top_dias_atipicos.iloc[0]['Mês'] # Get month from df_dias_atipicos for clarity

                # Defining a dictionary to map month numbers to names (if needed)
                meses_nome = {
                    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                }

                st.subheader(f"Análise Detalhada do Dia Mais Atípico: {dia_mais_atipico['Data']} (Score: {dia_mais_atipico['Score Atipicidade']:.2f})")
                st.markdown(f"""
                    Este gráfico de barras compara os valores do dia mais atípico (**{dia_mais_atipico['Data']}**)
                    com a média mensal histórica (para o mês {meses_nome.get(mes_do_dia_mais_atipico, str(mes_do_dia_mais_atipico))})
                    na região **{regiao_selecionada}**.
                    
                    **Propósito:** Entender *por que* esse dia foi considerado atípico, visualizando
                    quais variáveis (temperatura, umidade, radiação) se desviaram mais.
                    
                    **Interpretação:** Barras que se estendem muito acima ou abaixo da média indicam
                    a principal causa da atipicidade. Por exemplo, um dia com temperatura muito alta
                    e umidade muito baixa, ambos desviando da média, terá um score alto.
                    """)
                
                # Data for the comparative chart
                # Ensure medias_mes is correctly pulled
                # The merge in calcular_score_atipicidade already added the monthly_medias
                # So, we can directly get them from the dia_mais_atipico row
                
                # Retrieve the historical monthly averages from the original `df_dias_atipicos`
                # which has the `Temp_Media_Mensal` etc. columns
                monthly_historical_data = df_dias_atipicos[
                    (df_dias_atipicos['Mês'] == mes_do_dia_mais_atipico)
                ].iloc[0] # Take the first row for this month as it contains the monthly averages

                medias_mes = [
                    monthly_historical_data['Temp_Media_Mensal'],
                    monthly_historical_data['Umidade_Media_Mensal'],
                    monthly_historical_data['Radiacao_Media_Mensal']
                ]
                
                valores_dia_atipico = [
                    dia_mais_atipico['Temp. Média (°C)'],
                    dia_mais_atipico['Umid. Média (%)'],
                    dia_mais_atipico['Rad. Total (Kj/m²)']
                ]

                labels = ['Temperatura Média (°C)', 'Umidade Média (%)', 'Radiação Total (Kj/m²)']
                x = np.arange(len(labels))
                width = 0.35

                fig3, ax3 = plt.subplots(figsize=(10, 6))
                
                bars_dia = ax3.bar(x - width/2, valores_dia_atipico, width, label='Valor do Dia Atípico', color='darkorange')
                bars_media = ax3.bar(x + width/2, medias_mes, width, label=f'Média Mensal Histórica ({meses_nome.get(mes_do_dia_mais_atipico, str(mes_do_dia_mais_atipico))})', color='gray', alpha=0.7)

                ax3.set_ylabel('Valor', fontsize=12)
                ax3.set_title(f'Comparativo: Dia Atípico vs. Média Mensal - {dia_mais_atipico["Data"]}', fontsize=16)
                ax3.set_xticks(x)
                ax3.set_xticklabels(labels, rotation=15, ha='right')
                ax3.legend()
                ax3.grid(axis='y', linestyle='--', alpha=0.6)

                # Add values on bars
                for bar in bars_dia:
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=9)
                for bar in bars_media:
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=9, color='black', alpha=0.7)

                plt.tight_layout()
                st.pyplot(fig3)
            else:
                st.info("Não foi possível detalhar o dia mais atípico.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    # Captures the specific KeyError and tries to give a more friendly message
    st.error(f"Erro de Coluna: Uma das colunas esperadas não foi encontrada ou o nome está incorreto: '{e}'. Por favor, verifique se o seu arquivo CSV contém as colunas necessárias e se os nomes estão exatos (incluindo maiúsculas/minúsculas e espaços). As colunas críticas são: 'Ano', 'Mês', 'Regiao', 'Hora UTC' (opcional), 'RADIACAO GLOBAL (Kj/m²)', 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)', 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)', 'UMIDADE RELATIVA DO AR, HORARIA (%)' (ou o nome real da sua coluna de umidade).")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
