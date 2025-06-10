import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide")
st.title("Análise de Rajadas de Vento e Pressão Atmosférica (2020-2025)")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Converte colunas para numérico, tratando erros
    cols_to_numeric = [
        'Ano', 'Mês', 'Hora UTC', 'VENTO, RAJADA MAXIMA (m/s)',
        'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)',
        'PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)',
        'PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)'
    ]
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Criar uma coluna de variação de pressão horária
    if 'PRESSAO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)' in df.columns and \
       'PRESSAO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)' in df.columns:
        df['Variacao_Pressao_Horaria'] = df['PRESSAO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)'] - df['PRESSAO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)']
    else:
        df['Variacao_Pressao_Horaria'] = np.nan # Preenche com NaN se as colunas não existirem
        st.warning("Colunas de pressão máxima/mínima horária não encontradas. A análise de variação de pressão será limitada.")

    # Converte 'Data' para datetime
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    else:
        # Se 'Data' não existe, tenta criar uma do ano, mês, dia (se disponível)
        if all(col in df.columns for col in ['Ano', 'Mês']):
             # Assumir um dia padrão (ex: 15) se não houver coluna de dia, ou tentar usar dia do 'Data' se existir mas for string
            df['Dia_Temp'] = 1 # Cria um dia temporário para formar a data
            df['Data'] = pd.to_datetime(df[['Ano', 'Mês', 'Dia_Temp']].astype(str).agg('-'.join, axis=1), errors='coerce')
            df = df.drop(columns=['Dia_Temp'])
        else:
            st.warning("Coluna 'Data' e/ou 'Ano'/'Mês' não encontrada(s). A análise temporal pode ser limitada.")

    df = df.dropna(subset=['Ano', 'Mês', 'Hora UTC', 'VENTO, RAJADA MAXIMA (m/s)', 'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)', 'Variacao_Pressao_Horaria'])
    
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se as colunas essenciais para a análise existem
    if 'VENTO, RAJADA MAXIMA (m/s)' not in df_unificado.columns or \
       'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)' not in df_unificado.columns or \
       'Variacao_Pressao_Horaria' not in df_unificado.columns:
        st.error("Erro: Colunas essenciais para análise de vento e pressão não encontradas ou não puderam ser calculadas. Verifique seu arquivo CSV.")
        st.stop()

    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("---")
    st.header("Análise de Rajadas de Vento e Variações de Pressão Atmosférica")
    st.markdown("""
        Esta aplicação explora a relação entre **fortes rajadas de vento** e **mudanças na pressão atmosférica**,
        identificando quais regiões do Brasil são mais suscetíveis a esses eventos.
        Entender essa dinâmica é crucial para a previsão do tempo, segurança da infraestrutura e navegação.
        """)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Análise")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", regioes)

    # Limiar para Rajada de Vento Forte (ex: > 10 m/s = 36 km/h)
    limiar_rajada_vento = st.sidebar.slider(
        "Limiar para Rajada de Vento Forte (m/s):",
        min_value=5.0, max_value=30.0, value=15.0, step=1.0,
        help="Rajadas acima deste valor serão consideradas 'fortes'."
    )
    
    # Limiar para Variação de Pressão Significativa
    limiar_variacao_pressao = st.sidebar.slider(
        "Limiar para Variação de Pressão Significativa (mB/hora):",
        min_value=0.5, max_value=5.0, value=2.0, step=0.5,
        help="Variações absolutas de pressão horária acima deste valor indicam mudanças rápidas."
    )
    
    st.markdown("---")

    # --- PERGUNTA CENTRAL DA ANÁLISE ---
    st.subheader(f"Existe uma relação entre fortes rajadas de vento e mudanças na pressão atmosférica na Região {regiao_selecionada}?")
    st.markdown("""
        Esta seção investiga a conexão entre rajadas de vento intensas e as variações na pressão atmosférica,
        elementos frequentemente associados a sistemas meteorológicos mais ativos e mudanças climáticas.
        """)
    
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada].copy() # Usar .copy() para evitar SettingWithCopyWarning

    if df_regiao.empty:
        st.warning(f"Não foram encontrados dados para a Região {regiao_selecionada}.")
    else:
        # Calcular eventos de rajada forte
        df_regiao['Evento_Rajada_Forte'] = df_regiao['VENTO, RAJADA MAXIMA (m/s)'] >= limiar_rajada_vento
        
        # Calcular eventos de variação de pressão significativa
        df_regiao['Evento_Variacao_Pressao_Significativa'] = df_regiao['Variacao_Pressao_Horaria'].abs() >= limiar_variacao_pressao

        # Identificar eventos combinados
        df_regiao['Evento_Combinado'] = df_regiao['Evento_Rajada_Forte'] & df_regiao['Evento_Variacao_Pressao_Significativa']

        # --- GRÁFICO 1: FREQUÊNCIA DE EVENTOS COMBINADOS POR ANO ---
        st.subheader(f"1. Frequência Anual de Eventos com Rajadas Fortes e Variação de Pressão - {regiao_selecionada}")
        st.markdown(f"""
            Este gráfico de barras mostra o número de horas em cada ano onde ocorreram
            simultaneamente uma rajada de vento forte (≥ **{limiar_rajada_vento:.1f} m/s**)
            E uma variação significativa na pressão atmosférica (≥ **{limiar_variacao_pressao:.1f} mB/hora**)
            na região **{regiao_selecionada}**.
            
            **Propósito:** Identificar quais anos tiveram maior ocorrência de condições meteorológicas
            potencialmente severas ou transições rápidas de sistemas.
            
            **Interpretação:** Barras mais altas indicam anos com maior número de horas onde
            ambos os critérios foram atendidos. Isso pode sugerir anos com maior atividade
            de frentes frias, tempestades ou ciclones, que tipicamente envolvem ventos fortes
            e quedas/subidas rápidas de pressão.
            """)

        contagem_eventos_combinados = df_regiao.groupby('Ano')['Evento_Combinado'].sum().reindex(
            range(df_regiao['Ano'].min(), df_regiao['Ano'].max() + 1), fill_value=0
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        bar_colors = ['darkred' if count > 0 else 'lightgray' for count in contagem_eventos_combinados]
        bars = ax.bar(contagem_eventos_combinados.index.astype(int), contagem_eventos_combinados.values, color=bar_colors)

        ax.set_xlabel('Ano', fontsize=12)
        ax.set_ylabel('Número de Horas com Evento Combinado', fontsize=12)
        ax.set_title(f'Eventos Combinados (Rajada Forte e Variação Pressão) por Ano - {regiao_selecionada}', fontsize=14)
        ax.set_xticks(contagem_eventos_combinados.index.astype(int))
        ax.grid(axis='y', linestyle='--', alpha=0.6)

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, height, f'{int(height)}',
                         ha='center', va='bottom', color='black', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")

        # --- GRÁFICO 2: TOP 5 EVENTOS COMBINADOS (DATA/HORA) ---
        st.subheader(f"2. Top 5 Maiores Rajadas de Vento (m/s) e Variação de Pressão no Momento do Evento - {regiao_selecionada}")
        st.markdown(f"""
            Este gráfico de barras apresenta os 5 momentos (data e hora) em que as maiores rajadas de vento
            foram registradas na região, e compara a rajada com a variação de pressão atmosférica no mesmo horário.
            
            **Propósito:** Visualizar diretamente os eventos de vento mais extremos e verificar se houve
            uma variação de pressão notável associada a eles.
            
            **Interpretação:** Observar se as maiores rajadas de vento estão frequentemente ligadas a
            variações de pressão elevadas (positivas ou negativas). Isso pode indicar a passagem de
            sistemas meteorológicos intensos. Se as rajadas são altas mas a variação de pressão é baixa,
            outros fatores (como orografia) podem estar em jogo.
            """)
        
        # Filtra por rajadas acima de um mínimo para ter eventos relevantes, mesmo que não atinjam o limiar
        top_rajadas = df_regiao[df_regiao['VENTO, RAJADA MAXIMA (m/s)'] >= 10].nlargest(5, 'VENTO, RAJADA MAXIMA (m/s)')

        if not top_rajadas.empty:
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            
            # Criar rótulos para o eixo X com Data e Hora
            x_labels_top = top_rajadas.apply(lambda row: f"{row['Data'].strftime('%d/%m/%Y')} {int(row['Hora UTC']):02d}h", axis=1)

            # Eixo primário para Rajada de Vento
            ax2.bar(x_labels_top, top_rajadas['VENTO, RAJADA MAXIMA (m/s)'], color='teal', label='Rajada Máxima de Vento (m/s)')
            ax2.set_xlabel('Data e Hora (UTC)', fontsize=12)
            ax2.set_ylabel('Rajada Máxima de Vento (m/s)', color='teal', fontsize=12)
            ax2.tick_params(axis='y', labelcolor='teal')
            ax2.tick_params(axis='x', rotation=45, ha='right')

            # Eixo secundário para Variação de Pressão
            ax3 = ax2.twinx()
            ax3.plot(x_labels_top, top_rajadas['Variacao_Pressao_Horaria'], color='purple', marker='X', linestyle='-', linewidth=2, label='Variação Pressão Horária (mB)')
            ax3.set_ylabel('Variação de Pressão Horária (mB)', color='purple', fontsize=12)
            ax3.tick_params(axis='y', labelcolor='purple')

            ax2.set_title(f'Maiores Rajadas de Vento e Variação de Pressão - {regiao_selecionada}', fontsize=16)
            
            # Adicionar legendas de ambos os eixos
            lines, labels = ax2.get_legend_handles_labels()
            lines2, labels2 = ax3.get_legend_handles_labels()
            ax3.legend(lines + lines2, labels + labels2, loc='upper left')

            ax2.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info(f"Não há eventos de rajada de vento acima de 10 m/s para exibir os Top 5 na região {regiao_selecionada}.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada ou não pôde ser processada. Verifique se o seu arquivo contém os dados necessários e se os nomes das colunas estão corretos.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
