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
    col_mapping = {
        'Data': 'Data_Original', # Manter o nome original como backup se precisar
        'Hora UTC': 'Hora_UTC',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'Precipitacao_Total_Horaria',
        'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)': 'Pressao_Atmosferica_Horaria',
        'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)': 'Pressao_Maxima_Hora_Ant',
        'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)': 'Pressao_Minima_Hora_Ant',
        'RADIACAO GLOBAL (Kj/m²)': 'Radiacao_Global_Horaria',
        'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)': 'Temperatura_Bulbo_Seco_Horaria',
        'TEMPERATURA DO PONTO DE ORVALHO (°C)': 'Temperatura_Ponto_Orvalho_Horaria',
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': 'Temperatura_Maxima_Hora_Ant',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': 'Temperatura_Minima_Hora_Ant',
        'UMIDADE RELATIVA DO AR, HORARIA (%)': 'Umidade_Relativa_Horaria',
        'VENTO, RAJADA MAXIMA (m/s)': 'Vento_Rajada_Maxima',
        'VENTO, VELOCIDADE HORARIA (m/s)': 'Vento_Velocidade_Horaria',
        'Regiao': 'Regiao', # Já deve estar correto
        'Mês': 'Mês', # Já deve estar correto
        'Ano': 'Ano' # Já deve estar correto
        # Note: Algumas colunas da sua lista não são usadas diretamente nesta análise de atipicidade
    }
    
    # Aplica o mapeamento, ignorando chaves que não existem no DF
    df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})

    # --- Conversão de Tipos e Preparação de Dados ---
    
    # Combinar 'Data_Original' e 'Hora_UTC' em um único timestamp completo
    # Primeiro, garantir que 'Data_Original' é datetime
    if 'Data_Original' in df.columns:
        df['Data_Original'] = pd.to_datetime(df['Data_Original'], errors='coerce')
    else:
        st.error("Erro Crítico: Coluna 'Data' (originalmente 'Data') não encontrada. Esta análise depende dela.")
        st.stop() # Parar a execução se a coluna mais crucial não existe

    # Agora, combinar Data_Original com Hora_UTC para um timestamp completo
    # Assumimos que Hora_UTC é um inteiro representando a hora do dia (0-23)
    if 'Hora_UTC' in df.columns:
        df['Data_Hora_Completa'] = df.apply(lambda row: row['Data_Original'].replace(hour=int(row['Hora_UTC'])), axis=1)
    else:
        st.warning("Coluna 'Hora UTC' não encontrada. A análise diária será baseada apenas na data, não na hora exata.")
        df['Data_Hora_Completa'] = df['Data_Original'] # Se não tem hora, usa só a data

    # Remover linhas com NaN em colunas críticas após conversão
    df = df.dropna(subset=[
        'Data_Hora_Completa', 'Regiao', 'Mês', 'Ano',
        'Temperatura_Bulbo_Seco_Horaria',
        'Umidade_Relativa_Horaria',
        'Radiacao_Global_Horaria'
    ])

    # Agrupar por dia, região, mês, ano para obter valores diários
    # Usaremos a Data_Original para agrupar por dia calendário
    df_diario = df.groupby(['Data_Original', 'Regiao', 'Mês', 'Ano']).agg(
        Temp_Media_Diaria=('Temperatura_Bulbo_Seco_Horaria', 'mean'),
        Umidade_Media_Diaria=('Umidade_Relativa_Horaria', 'mean'),
        Radiacao_Total_Diaria=('Radiacao_Global_Horaria', 'sum') # Radiação é acumulada no dia
    ).reset_index()

    return df_diario

# --- CÁLCULO DO SCORE DE ATIPICIDADE ---
def calcular_score_atipicidade(df_diario_regiao):
    """
    Calcula um score de atipicidade para cada dia, baseado nos desvios padrão
    das variáveis em relação à média mensal histórica daquela região.
    """
    df_scores = df_diario_regiao.copy()
    
    # Calcular médias e desvios padrão mensais históricos para cada variável
    historico_mensal = df_scores.groupby(['Mês']).agg(
        Temp_Media_Mensal=('Temp_Media_Diaria', 'mean'),
        Temp_Std_Mensal=('Temp_Media_Diaria', 'std'),
        Umidade_Media_Mensal=('Umidade_Media_Diaria', 'mean'),
        Umidade_Std_Mensal=('Umidade_Media_Diaria', 'std'),
        Radiacao_Media_Mensal=('Radiacao_Total_Diaria', 'mean'),
        Radiacao_Std_Mensal=('Radiacao_Total_Diaria', 'std')
    )
    
    # Merge com os dados diários para cálculo do Z-score
    df_scores = df_scores.merge(historico_mensal, on='Mês', how='left')

    # Calcular Z-scores (número de desvios padrão da média)
    # Adiciona um pequeno valor para evitar divisão por zero se std for 0
    epsilon = 1e-6 
    df_scores['Z_Temp'] = (df_scores['Temp_Media_Diaria'] - df_scores['Temp_Media_Mensal']) / (df_scores['Temp_Std_Mensal'] + epsilon)
    df_scores['Z_Umidade'] = (df_scores['Umidade_Media_Diaria'] - df_scores['Umidade_Media_Mensal']) / (df_scores['Umidade_Std_Mensal'] + epsilon)
    df_scores['Z_Radiacao'] = (df_scores['Radiacao_Total_Diaria'] - df_scores['Radiacao_Media_Mensal']) / (df_scores['Radiacao_Std_Mensal'] + epsilon)

    # Calcular um score combinado de atipicidade (magnitude do desvio)
    # Usamos o valor absoluto do Z-score e somamos
    df_scores['Score_Atipicidade'] = df_scores['Z_Temp'].abs() + df_scores['Z_Umidade'].abs() + df_scores['Z_Radiacao'].abs()
    
    # Tratar NaN resultantes de std=0 ou dados faltantes (se for o caso)
    df_scores['Score_Atipicidade'] = df_scores['Score_Atipicidade'].fillna(0) # Tratar dias onde o calculo do score falhou, talvez por falta de dados suficientes para std

    return df_scores.sort_values(by='Score_Atipicidade', ascending=False)


# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_diario_unificado = carregar_dados(caminho_arquivo_unificado)
    
    if df_diario_unificado.empty:
        st.error("Não foi possível carregar ou processar os dados diários. Verifique seu arquivo CSV e as colunas.")
        st.stop()

    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("---")
    st.header("Identificando Dias Climáticos 'Incomuns' por Região")
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
            
            # Formatar para exibição
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
                mes_do_dia_mais_atipico = dia_mais_atipico['Mês']

                # Definindo um dicionário para mapear números de mês para nomes (se necessário)
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
                
                # Dados para o gráfico comparativo
                # Certifique-se de que medias_mes está sendo puxado corretamente
                # O merge em calcular_score_atipicidade já adicionou as medias_mensais
                # Então, podemos pegá-las diretamente da linha do dia_mais_atipico
                medias_mes = dia_mais_atipico[[
                    'Temp_Media_Mensal', 'Umidade_Media_Mensal', 'Radiacao_Media_Mensal'
                ]].values
                
                valores_dia_atipico = dia_mais_atipico[[
                    'Temp. Média (°C)', 'Umid. Média (%)', 'Rad. Total (Kj/m²)'
                ]].values

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

                # Adicionar valores nas barras
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
    # Captura o KeyError específico e tenta dar uma mensagem mais amigável
    st.error(f"Erro de Coluna: Uma das colunas esperadas não foi encontrada ou o nome está incorreto: '{e}'. Por favor, verifique se o seu arquivo CSV contém as seguintes colunas e se os nomes estão exatos (incluindo maiúsculas/minúsculas e espaços): {list(col_mapping.keys())}")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
