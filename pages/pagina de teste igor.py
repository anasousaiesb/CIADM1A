import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide", page_title="Análise Climática Regional")
st.title("Análise Climática Regional do Brasil (2020-2025)")
st.markdown("Bem-vindo à ferramenta de análise climática. Selecione uma região e uma variável para explorar padrões e atipicidades.")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """
    Carrega e processa o arquivo de dados climáticos,
    calculando médias/somas diárias e amplitude térmica.
    """
    df = pd.read_csv(caminho)

    # --- Renomear colunas para facilitar o uso no código ---
    col_mapping = {
        'Hora UTC': 'Hora_UTC',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'Precipitacao_Total_Horaria',
        'RADIACAO GLOBAL (Kj/m²)': 'Radiacao_Global_Horaria',
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': 'Temperatura_Maxima_Hora_Ant',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': 'Temperatura_Minima_Hora_Ant',
        # >>>>> ATENÇÃO AQUI: INSIRA O NOME EXATO DA COLUNA DE UMIDADE DO SEU CSV <<<<<
        # EX: Se o nome real for 'UMIDADE DO AR', mude a chave abaixo para: 'UMIDADE DO AR': 'Umidade_Relativa_Horaria',
        'UMIDADE RELATIVA DO AR, HORARIA (%)': 'Umidade_Relativa_Horaria', # <-- ***MUDE ESTA CHAVE***
        'Regiao': 'Regiao',
        'Mês': 'Mês',
        'Ano': 'Ano'
    }
    
    df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})

    # Ensure 'Ano' and 'Mês' are available and numeric
    if 'Ano' not in df.columns or 'Mês' not in df.columns:
        st.error("Erro Crítico: Colunas 'Ano' ou 'Mês' não encontradas para construir a data. Verifique os nomes das colunas em seu CSV.")
        st.stop()
    
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df = df.dropna(subset=['Ano', 'Mês'])

    # --- Construct 'Data_Original' for daily grouping ---
    if 'Data' in df.columns:
        df['Data_Original'] = pd.to_datetime(df['Data'], errors='coerce')
    elif 'Dia' in df.columns: 
        df['Dia'] = pd.to_numeric(df['Dia'], errors='coerce')
        df['Data_Original'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mês'].astype(str) + '-' + df['Dia'].astype(str), errors='coerce')
    else:
        # Default to 1st of month if no specific day column is found.
        df['Data_Original'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mês'].astype(str) + '-01', errors='coerce')
        st.warning("Coluna 'Data' ou 'Dia' não encontrada. A data será construída usando o primeiro dia do mês. Isso pode afetar a precisão da amplitude térmica diária se os dados originais forem horários sem um dia explícito.")
    
    # Combine 'Data_Original' and 'Hora_UTC' if available
    if 'Hora_UTC' in df.columns:
        df['Hora_UTC'] = pd.to_numeric(df['Hora_UTC'], errors='coerce').fillna(0).astype(int)
        df['Data_Hora_Completa'] = df.apply(lambda row: row['Data_Original'].replace(hour=row['Hora_UTC']) if pd.notna(row['Data_Original']) else pd.NaT, axis=1)
    else:
        st.warning("Coluna 'Hora UTC' não encontrada. A análise diária será baseada apenas na data, não na hora exata.")
        df['Data_Hora_Completa'] = df['Data_Original']

    # --- Ensure critical temperature columns exist and are numeric ---
    temp_cols_missing = False
    if 'Temperatura_Maxima_Hora_Ant' not in df.columns:
        st.error("Erro Crítico: Coluna 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' não encontrada. É necessária para cálculos de temperatura.")
        temp_cols_missing = True
    if 'Temperatura_Minima_Hora_Ant' not in df.columns:
        st.error("Erro Crítico: Coluna 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' não encontrada. É necessária para cálculos de temperatura.")
        temp_cols_missing = True
    if temp_cols_missing:
        st.stop()
    
    df['Temperatura_Maxima_Hora_Ant'] = pd.to_numeric(df['Temperatura_Maxima_Hora_Ant'], errors='coerce')
    df['Temperatura_Minima_Hora_Ant'] = pd.to_numeric(df['Temperatura_Minima_Hora_Ant'], errors='coerce')
    
    # Check for Umidade_Relativa_Horaria. If missing, warn and create NaN column.
    if 'Umidade_Relativa_Horaria' not in df.columns:
        st.warning("Coluna 'Umidade_Relativa_Horaria' não encontrada. A umidade será excluída da análise de atipicidade e de gráficos que a utilizem.")
        df['Umidade_Relativa_Horaria'] = np.nan # Create a dummy NaN column

    # Calculate Temp_Media_Horaria for daily mean aggregation
    df['Temp_Media_Horaria'] = (df['Temperatura_Maxima_Hora_Ant'] + df['Temperatura_Minima_Hora_Ant']) / 2

    # --- Aggregate to Daily Data (df_diario) ---
    df_diario = df.groupby(['Data_Original', 'Regiao', 'Mês', 'Ano']).agg(
        Temp_Maxima_Diaria=('Temperatura_Maxima_Hora_Ant', 'max'),
        Temp_Minima_Diaria=('Temperatura_Minima_Hora_Ant', 'min'),
        Temp_Media_Diaria=('Temp_Media_Horaria', 'mean'), 
        Precipitacao_Total_Diaria=('Precipitacao_Total_Horaria', 'sum'),
        Radiacao_Total_Diaria=('Radiacao_Global_Horaria', 'sum'),
        Umidade_Media_Diaria=('Umidade_Relativa_Horaria', 'mean') # Will be NaN if original column was missing
    ).reset_index()

    # Calculate daily thermal amplitude
    df_diario['Amplitude_Termica_Diaria'] = df_diario['Temp_Maxima_Diaria'] - df_diario['Temp_Minima_Diaria']
    
    # Drop rows with NaN in critical daily columns (after all calculations)
    df_diario = df_diario.dropna(subset=[
        'Data_Original', 'Regiao', 'Mês', 'Ano',
        'Temp_Media_Diaria',
        'Precipitacao_Total_Diaria',
        'Radiacao_Total_Diaria',
        'Amplitude_Termica_Diaria'
    ])
    
    # If Umidade_Media_Diaria is all NaN after aggregation, drop the column
    if 'Umidade_Media_Diaria' in df_diario.columns and df_diario['Umidade_Media_Diaria'].isnull().all():
        df_diario = df_diario.drop(columns=['Umidade_Media_Diaria'])

    return df_diario

# --- CÁLCULO DO SCORE DE ATIPICIDADE (Ajustado para o novo df_diario) ---
def calcular_score_atipicidade(df_diario_regiao):
    """
    Calcula um score de atipicidade para cada dia, baseado nos desvios padrão
    das variáveis em relação à média mensal histórica daquela região.
    """
    df_scores = df_diario_regiao.copy()
    
    agg_funcs = {
        'Temp_Media_Mensal': ('Temp_Media_Diaria', 'mean'),
        'Temp_Std_Mensal': ('Temp_Media_Diaria', 'std'),
        'Radiacao_Media_Mensal': ('Radiacao_Total_Diaria', 'mean'),
        'Radiacao_Std_Mensal': ('Radiacao_Total_Diaria', 'std')
    }
    
    if 'Umidade_Media_Diaria' in df_scores.columns:
        agg_funcs['Umidade_Media_Mensal'] = ('Umidade_Media_Diaria', 'mean')
        agg_funcs['Umidade_Std_Mensal'] = ('Umidade_Media_Diaria', 'std')

    historico_mensal = df_scores.groupby(['Mês']).agg(**agg_funcs)
    
    df_scores = df_scores.merge(historico_mensal, on='Mês', how='left')

    epsilon = 1e-6 
    df_scores['Z_Temp'] = (df_scores['Temp_Media_Diaria'] - df_scores['Temp_Media_Mensal']) / (df_scores['Temp_Std_Mensal'] + epsilon)
    df_scores['Z_Radiacao'] = (df_scores['Radiacao_Total_Diaria'] - df_scores['Radiacao_Media_Mensal']) / (df_scores['Radiacao_Std_Mensal'] + epsilon)

    score_contributions = [df_scores['Z_Temp'].abs(), df_scores['Z_Radiacao'].abs()]

    if 'Umidade_Media_Diaria' in df_scores.columns and 'Umidade_Std_Mensal' in df_scores.columns and not df_scores['Umidade_Std_Mensal'].isnull().all():
        df_scores['Z_Umidade'] = (df_scores['Umidade_Media_Diaria'] - df_scores['Umidade_Media_Mensal']) / (df_scores['Umidade_Std_Mensal'] + epsilon)
        score_contributions.append(df_scores['Z_Umidade'].abs())
    else:
        df_scores['Z_Umidade'] = 0 

    df_scores['Score_Atipicidade'] = sum(score_contributions)
    df_scores['Score_Atipicidade'] = df_scores['Score_Atipicidade'].fillna(0)

    return df_scores.sort_values(by='Score_Atipicidade', ascending=False)


# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_diario_unificado = carregar_dados(caminho_arquivo_unificado)
    
    if df_diario_unificado.empty:
        st.error("Não foi possível carregar ou processar os dados diários. Verifique seu arquivo CSV e as colunas.")
        st.stop()

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Visualização")
    
    regioes = sorted(df_diario_unificado['Regiao'].unique())
    regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", regioes)

    # Adicionando Amplitude_Termica_Diaria como variável selecionável
    variaveis = {
        'Temperatura Média Diária (°C)': 'Temp_Media_Diaria',
        'Amplitude Térmica Diária (°C)': 'Amplitude_Termica_Diaria', # Nova variável
        'Precipitação Total Diária (mm)': 'Precipitacao_Total_Diaria',
        'Radiação Global Total (Kj/m²)': 'Radiacao_Total_Diaria'
    }
    if 'Umidade_Media_Diaria' in df_diario_unificado.columns:
        variaveis['Umidade Média Diária (%)'] = 'Umidade_Media_Diaria'
        
    nome_var = st.sidebar.selectbox("Selecione a Variável para Análise Anual:", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]
    unidade_var = nome_var.split('(')[-1].replace(')', '') if '(' in nome_var else ''

    # --- VISUALIZAÇÃO PRINCIPAL (Sazonalidade Anual para a variável selecionada) ---
    st.header(f"Comparativo Anual de {nome_var} na Região {regiao_selecionada}")
    st.markdown("Este gráfico mostra a variação média mensal da variável selecionada para cada ano no período, comparada à média histórica.")

    cmap = get_cmap('plasma')
    anos_disponiveis = sorted(df_diario_unificado['Ano'].unique())
    cores_anos = {ano: cmap(i / (len(anos_disponiveis) -1 if len(anos_disponiveis) > 1 else 1)) for i, ano in enumerate(anos_disponiveis)}

    df_regiao_diario = df_diario_unificado[df_diario_unificado['Regiao'] == regiao_selecionada]

    fig_sazonal, ax_sazonal = plt.subplots(figsize=(12, 6))

    valores_anuais_por_mes = {}
    for ano in anos_disponiveis:
        df_ano_regiao = df_regiao_diario[df_regiao_diario['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        if not df_ano_regiao.empty:
            ax_sazonal.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos.get(ano, 'gray'), label=str(int(ano)))
        valores_anuais_por_mes[ano] = df_ano_regiao.values

    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    ax_sazonal.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='black', label=f'Média Histórica ({int(min(anos_disponiveis))}-{int(max(anos_disponiveis))})', linewidth=2.5)

    ax_sazonal.set_title(f'Variação Mensal de {nome_var} por Ano - {regiao_selecionada}', fontsize=16)
    ax_sazonal.set_xlabel('Mês', fontsize=12)
    ax_sazonal.set_ylabel(nome_var, fontsize=12)
    ax_sazonal.set_xticks(range(1, 13))
    ax_sazonal.grid(True, linestyle='--', alpha=0.6)
    ax_sazonal.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig_sazonal)
    
    st.markdown("---")

    ## Análise de Amplitude Térmica Diária
    st.header("Análise Detalhada: Amplitude Térmica Diária")
    st.markdown("""
        Esta seção oferece um olhar aprofundado sobre a **amplitude térmica diária**
        (a diferença entre a temperatura máxima e mínima do dia). Entender como essa
        variável se comporta é crucial para compreender a variabilidade climática local,
        pois grandes amplitudes podem indicar dias com céu limpo e baixa umidade,
        permitindo forte aquecimento diurno e resfriamento noturno.
        """)
    
    # Plot 1: Box Plot da Amplitude Térmica por Mês
    st.subheader("Distribuição Mensal da Amplitude Térmica Diária")
    st.markdown("O box plot mostra a distribuição (mediana, quartis e outliers) da amplitude térmica para cada mês na região selecionada.")
    
    fig_box, ax_box = plt.subplots(figsize=(12, 6))
    
    amplitude_por_mes = [df_regiao_diario[df_regiao_diario['Mês'] == m]['Amplitude_Termica_Diaria'].dropna() for m in range(1, 13)]
    
    valid_months = [m for m, data in enumerate(amplitude_por_mes, 1) if not data.empty]
    valid_amplitude_data = [data for data in amplitude_por_mes if not data.empty]

    if valid_amplitude_data:
        ax_box.boxplot(valid_amplitude_data, labels=valid_months, patch_artist=True, medianprops={'color': 'red'})
        ax_box.set_title(f'Distribuição da Amplitude Térmica Diária por Mês - {regiao_selecionada}', fontsize=16)
        ax_box.set_xlabel('Mês', fontsize=12)
        ax_box.set_ylabel('Amplitude Térmica Diária (°C)', fontsize=12)
        ax_box.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_box)
        
        st.markdown("""
            **Interpretação:** Meses com caixas maiores indicam maior **variabilidade** na amplitude térmica diária. Outliers (pontos fora das 'hastes') representam dias com oscilações de temperatura excepcionalmente altas ou baixas.
            """)
    else:
        st.info("Dados de amplitude térmica diária insuficientes para gerar o box plot mensal.")

    st.markdown("---")

    # Plot 2: Média Anual da Amplitude Térmica Diária
    st.subheader("Média Anual da Amplitude Térmica Diária")
    st.markdown("Este gráfico de linha apresenta a média da amplitude térmica diária para cada ano no período analisado.")
    fig_line_yearly, ax_line_yearly = plt.subplots(figsize=(10, 5))
    
    media_amplitude_anual = df_regiao_diario.groupby('Ano')['Amplitude_Termica_Diaria'].mean()
    
    if not media_amplitude_anual.empty:
        ax_line_yearly.plot(media_amplitude_anual.index, media_amplitude_anual.values, marker='o', linestyle='-', color='purple')
        ax_line_yearly.set_title(f'Média Anual da Amplitude Térmica Diária - {regiao_selecionada}', fontsize=16)
        ax_line_yearly.set_xlabel('Ano', fontsize=12)
        ax_line_yearly.set_ylabel('Média da Amplitude Térmica Diária (°C)', fontsize=12)
        ax_line_yearly.set_xticks(media_amplitude_anual.index.astype(int))
        ax_line_yearly.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_line_yearly)

        st.markdown("""
            **Interpretação:** Observe se há picos ou vales notáveis, que podem indicar anos com maior ou menor intensidade de variação térmica diária. Isso pode estar relacionado a fenômenos climáticos mais amplos.
            """)
    else:
        st.info("Dados de amplitude térmica diária insuficientes para gerar o gráfico de média anual.")

    st.markdown("---")
    
    # Análise textual para meses/anos com variações mais acentuadas
    st.subheader("Meses e Anos com Variações de Amplitude Mais Acentuadas")
    if not df_regiao_diario.empty:
        median_amplitude_by_month = df_regiao_diario.groupby('Mês')['Amplitude_Termica_Diaria'].median()
        mean_amplitude_by_year = df_regiao_diario.groupby('Ano')['Amplitude_Termica_Diaria'].mean()

        if not median_amplitude_by_month.empty:
            max_median_month = median_amplitude_by_month.idxmax()
            st.write(f"- O mês com a maior mediana de amplitude térmica diária na região **{regiao_selecionada}** é o **{max_median_month}**.")
        
        if not mean_amplitude_by_year.empty:
            max_mean_year = mean_amplitude_by_year.idxmax()
            st.write(f"- O ano com a maior média de amplitude térmica diária é o **{int(max_mean_year)}**.")

        st.markdown("""
            Essas observações podem indicar **padrões sazonais** (ex: meses mais secos e com céu limpo) ou **tendências anuais** (ex: anos com maior incidência de frentes frias ou massas de ar seco) que levam a grandes oscilações de temperatura dentro de um mesmo dia. Uma amplitude térmica diária elevada, por exemplo, pode ser associada a dias quentes e noites frias.
            """)
    else:
        st.info("Não foi possível realizar a análise de meses e anos com variações mais acentuadas devido à falta de dados.")


    st.markdown("---")

    ## Formulação de Hipóteses
    st.header("Que hipóteses sobre o clima futuro podem ser formuladas com base nestes dados?")
    st.warning("🚨 **Aviso:** A análise a seguir baseia-se em dados de curto prazo (2020-2025). As 'tendências' e 'hipóteses' são exercícios exploratórios e **não devem ser consideradas previsões climáticas definitivas**, que exigem séries de dados de décadas.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hipótese 1: Análise de Tendência Anual")
        media_anual = df_regiao_diario.groupby('Ano')[coluna_var].mean().dropna()
        
        if len(media_anual) > 1:
            anos_validos = media_anual.index.astype(int)
            valores_validos = media_anual.values

            slope, intercept = np.polyfit(anos_validos, valores_validos, 1)
            trend_line = slope * anos_validos + intercept
            
            fig_trend, ax_trend = plt.subplots(figsize=(6, 4))
            ax_trend.plot(anos_validos, valores_validos, marker='o', linestyle='-', label='Média Anual Observada')
            ax_trend.plot(anos_validos, trend_line, linestyle='--', color='red', label='Linha de Tendência')
            ax_trend.set_title(f'Tendência Anual de {nome_var}')
            ax_trend.set_xlabel('Ano')
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})')
            ax_trend.grid(True, linestyle='--', alpha=0.5)
            ax_trend.legend()
            plt.tight_layout()
            st.pyplot(fig_trend)

            tendencia_texto = ""
            if slope > 0.05:
                tendencia_texto = f"**Tendência de Aumento:** Os dados sugerem uma tendência de **aumento** para a {nome_var.lower()} na região {regiao_selecionada}. A uma taxa de `{slope:.3f} {unidade_var}/ano`, a hipótese é de que a região pode enfrentar **condições progressivamente mais quentes/chuvosas/irradiadas** se essa tendência de curto prazo continuar."
            elif slope < -0.05:
                tendencia_texto = f"**Tendência de Diminuição:** Os dados sugerem uma tendência de **diminuição** para a {nome_var.lower()} na região {regiao_selecionada}. A uma taxa de `{slope:.3f} {unidade_var}/ano`, a hipótese é de que a região pode estar se tornando **mais fria/seca/com menos radiação** se essa tendência de curto prazo persistir."
            else:
                tendencia_texto = f"**Tendência de Estabilidade:** A linha de tendência é quase plana (`{slope:.3f} {unidade_var}/ano`), sugerindo **relativa estabilidade** na média anual de {nome_var.lower()} na região {regiao_selecionada} durante este período. A hipótese principal seria a manutenção das condições médias atuais, mas com atenção à variabilidade entre os anos."
            
            st.markdown(tendencia_texto)

        else:
            st.info("Dados insuficientes (menos de 2 anos) para calcular uma tendência.")

    with col2:
        st.subheader("Hipótese 2: Análise de Variabilidade")
        
        monthly_avg_for_var = df_regiao_diario.groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
        annual_monthly_data = df_regiao_diario.pivot_table(index='Mês', columns='Ano', values=coluna_var)
        desvios_abs_anuais = (annual_monthly_data.subtract(monthly_avg_for_var, axis=0)).abs().mean().dropna()

        if not desvios_abs_anuais.empty:
            ano_mais_atipico = desvios_abs_anuais.idxmax()
            maior_desvio = desvios_abs_anuais.max()
            
            st.markdown(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
            st.markdown(f"- O ano de **{int(ano_mais_atipico)}** se destaca como o **mais atípico** (ou extremo), com as médias mensais se afastando em média **{maior_desvio:.2f} {unidade_var}** da média histórica do período.")
            
            st.markdown("**Hipótese de Variabilidade:** Se os anos mais recentes (ex: 2024, 2025) aparecem consistentemente com os maiores desvios, isso pode sugerir uma hipótese de que **o clima na região está se tornando mais variável e propenso a extremos**. Anos que se desviam significativamente da média (para cima ou para baixo) podem se tornar mais frequentes.")

            st.write("**Ranking de Anos por Desvio (Atipicidade):**")
            desvios_df = pd.DataFrame(desvios_abs_anuais, columns=['Desvio Médio Absoluto'])
            st.dataframe(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).style.format("{:.2f}"))
        else:
            st.info("Não há dados suficientes para realizar a análise de variabilidade anual.")

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a variável selecionada e se o 'col_mapping' está correto.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução: {e}")
