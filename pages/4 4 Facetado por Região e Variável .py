import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
# TÍTULO: Mesmo que não seja Streamlit, ajuda a identificar a análise
print("--- Análise de Amplitude Térmica Diária Regional (2020-2025) ---")

# Caminho relativo ao arquivo CSV que VOCÊ tem.
# Ajuste este caminho e nome do arquivo para O SEU CSV.
# Por exemplo: "meus_dados_climaticos.csv" ou "dados/clima/meu_arquivo.csv"
caminho_arquivo_do_usuario = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
def carregar_dados_seguro(caminho):
    """
    Tenta carregar e processar o arquivo de dados climáticos.
    Retorna um DataFrame processado ou um DataFrame de exemplo se o arquivo não for encontrado
    ou não tiver as colunas esperadas.
    """
    df = pd.DataFrame() # DataFrame vazio padrão

    try:
        df = pd.read_csv(caminho)
        print(f"Arquivo '{os.path.basename(caminho)}' carregado com sucesso.")
    except FileNotFoundError:
        print(f"AVISO: Arquivo '{os.path.basename(caminho)}' NÃO ENCONTRADO.")
        print("Criando DataFrame de EXEMPLO para demonstrar o código.")
        print("Por favor, substitua os dados de exemplo pelos seus dados reais para uma análise significativa.")
        # DataFrame de exemplo para que o código continue rodando
        data_exemplo = {
            'Regiao': ['SUDESTE', 'SUDESTE', 'SUDESTE', 'SUDESTE', 'SUDESTE', 'SUDESTE', 'NORTE', 'NORTE'],
            'Ano': [2020, 2020, 2021, 2021, 2022, 2022, 2020, 2020],
            'Mês': [1, 7, 1, 7, 1, 7, 1, 7],
            'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': [30.0, 25.0, 31.0, 24.0, 29.5, 26.0, 35.0, 32.0],
            'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': [20.0, 15.0, 20.0, 14.0, 19.0, 16.0, 25.0, 20.0],
            'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': [50.0, 10.0, 60.0, 5.0, 45.0, 12.0, 200.0, 150.0],
            'RADIACAO GLOBAL (Kj/m²)': [1000, 500, 1100, 450, 950, 550, 800, 700]
        }
        df = pd.DataFrame(data_exemplo)

    # --- Verificação e cálculo de colunas essenciais ---
    col_max_temp = 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'
    col_min_temp = 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'

    if col_max_temp in df.columns and col_min_temp in df.columns:
        df['Temp_Media'] = (df[col_max_temp] + df[col_min_temp]) / 2
        df['Amplitude_Termica'] = df[col_max_temp] - df[col_min_temp]
        print("Colunas 'Temp_Media' e 'Amplitude_Termica' calculadas.")
    else:
        print(f"AVISO: As colunas '{col_max_temp}' e/ou '{col_min_temp}' não foram encontradas no DataFrame.")
        print("Não foi possível calcular 'Temp_Media' e 'Amplitude_Termica'.")
        # Se as colunas não existem e não podem ser calculadas, forçamos o erro para parar
        # ou retornamos um DataFrame vazio para evitar mais erros.
        return pd.DataFrame()

    # --- Conversão e limpeza ---
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano', 'Amplitude_Termica']) # Garante dados completos para a análise

    return df

# --- CARREGAMENTO DOS DADOS (AGORA MAIS SEGURO) ---
df_analise = carregar_dados_seguro(caminho_arquivo_do_usuario)

if df_analise.empty:
    print("\nERRO CRÍTICO: Não foi possível obter dados válidos para a análise. Verifique o arquivo CSV e os nomes das colunas.")
else:
    # --- INTERFACE (SIMULADA COM PRINT/PLOT) ---
    regioes_disponiveis = sorted(df_analise['Regiao'].unique())
    anos_disponiveis = sorted(df_analise['Ano'].unique())

    print("\n--- Seleção de Parâmetros de Análise ---")
    print(f"Regiões disponíveis: {regioes_disponiveis}")
    # Para o exemplo, vamos escolher a primeira região disponível ou uma específica
    regiao_selecionada = 'SUDESTE' if 'SUDESTE' in regioes_disponiveis else regioes_disponiveis[0]
    print(f"Região selecionada para análise: {regiao_selecionada}")

    # A variável principal de interesse para esta análise é a Amplitude Térmica
    coluna_var = 'Amplitude_Termica'
    nome_var = 'Amplitude Térmica Diária (°C)'
    unidade_var = '°C'

    # --- VISUALIZAÇÃO 1: Comparativo Anual da Média Mensal de Amplitude Térmica ---
    print(f"\nGerando 'Variação Mensal da Média de {nome_var} por Ano na Região {regiao_selecionada}'...")

    df_regiao = df_analise[df_analise['Regiao'] == regiao_selecionada].copy()

    if df_regiao.empty:
        print(f"AVISO: Não há dados para a região '{regiao_selecionada}' após a filtragem.")
    else:
        fig1, ax1 = plt.subplots(figsize=(12, 6))

        cmap = get_cmap('plasma')
        # Ajusta o cmap para o número de anos disponíveis na região específica
        cores_anos = {ano: cmap(i / (len(anos_disponiveis) - 1 if len(anos_disponiveis) > 1 else 1)) for i, ano in enumerate(anos_disponiveis)}

        valores_anuais_por_mes = {}
        for ano in anos_disponiveis:
            # Calcula a média mensal da amplitude térmica para cada ano
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(range(1, 13))
            if not df_ano_regiao.empty:
                ax1.plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos.get(ano, 'gray'), label=str(int(ano)))
            valores_anuais_por_mes[ano] = df_ano_regiao.values

        df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=range(1, 13))
        # Remove colunas de anos que não tinham dados (NaNs em todas as linhas)
        df_valores_anuais = df_valores_anuais.dropna(axis=1, how='all')

        if not df_valores_anuais.empty:
            media_historica_mensal = df_valores_anuais.mean(axis=1)
            ax1.plot(media_historica_mensal.index, media_historica_mensal.values, linestyle='--', color='black', label=f'Média Histórica ({int(min(anos_disponiveis))}-{int(max(anos_disponiveis))})', linewidth=2.5)

            ax1.set_title(f'Variação Mensal da Média de {nome_var} por Ano - {regiao_selecionada}', fontsize=16)
            ax1.set_xlabel('Mês', fontsize=12)
            ax1.set_ylabel(nome_var, fontsize=12)
            ax1.set_xticks(range(1, 13))
            ax1.grid(True, linestyle='--', alpha=0.6)
            ax1.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show() # Mostra o primeiro gráfico
        else:
            print("AVISO: Sem dados suficientes para plotar a variação mensal por ano.")

    # --- VISUALIZAÇÃO 2: Distribuição Mensal da Amplitude Térmica (Box Plot) ---
    print(f"\nGerando 'Distribuição Mensal da {nome_var} na Região {regiao_selecionada}' (Box Plot)...")

    if not df_regiao.empty:
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        df_regiao.boxplot(column=coluna_var, by='Mês', ax=ax2, grid=True)
        ax2.set_title(f'Distribuição da Amplitude Térmica Diária por Mês - {regiao_selecionada}')
        ax2.set_xlabel('Mês')
        ax2.set_ylabel(nome_var)
        plt.suptitle('') # Suptitle é adicionado automaticamente pelo boxplot e pode ser redundante
        plt.tight_layout()
        plt.show() # Mostra o segundo gráfico

        print("""
        Este gráfico de caixa (boxplot) mostra a distribuição da amplitude térmica diária para cada mês.
        - **Linha central**: Mediana.
        - **Caixas**: Intervalo interquartil (IQR), 50% dos dados. Caixas mais longas = maior variabilidade.
        - **"Barbas"**: Mínimo/máximo dentro de 1.5x IQR.
        - **Pontos (outliers)**: Valores atípicos, grandes variações.
        **Meses com caixas e/ou "barbas" mais longas, e mais outliers, apresentam variações mais acentuadas.**
        """)
    else:
        print("AVISO: Sem dados para a região selecionada para gerar o Box Plot.")


    # --- FORMULAÇÃO DE HIPÓTESES ---
    print("\n--- Formulação de Hipóteses (Baseada na Amplitude Térmica Diária) ---")
    print("🚨 Aviso: A análise a seguir baseia-se em dados de curto prazo (2020-2025). As 'tendências' e 'hipóteses' são exercícios exploratórios e NÃO devem ser consideradas previsões climáticas definitivas.")

    if not df_valores_anuais.empty:
        # --- HIPÓTESE 1: ANÁLISE DE TENDÊNCIA ANUAL ---
        print("\n**Hipótese 1: Análise de Tendência Anual**")

        media_anual = df_valores_anuais.mean(axis=0).dropna()

        if len(media_anual) > 1:
            anos_para_tendencia = media_anual.index.astype(int)
            valores_para_tendencia = media_anual.values

            slope, intercept = np.polyfit(anos_para_tendencia, valores_para_tendencia, 1)
            trend_line = slope * anos_para_tendencia + intercept

            fig_trend, ax_trend = plt.subplots(figsize=(6, 4))
            ax_trend.plot(anos_para_tendencia, valores_para_tendencia, marker='o', linestyle='-', label='Média Anual Observada')
            ax_trend.plot(anos_para_tendencia, trend_line, linestyle='--', color='red', label='Linha de Tendência')
            ax_trend.set_title(f'Tendência Anual da Média de {nome_var}')
            ax_trend.set_xlabel('Ano')
            ax_trend.set_ylabel(f'Média Anual ({unidade_var})')
            ax_trend.grid(True, linestyle='--', alpha=0.5)
            ax_trend.legend()
            plt.tight_layout()
            plt.show() # Mostra o gráfico de tendência

            tendencia_texto = ""
            if slope > 0.05:
                tendencia_texto = f"**Tendência de Aumento:** Os dados sugerem um **aumento** na {nome_var.lower()} na região {regiao_selecionada} ({slope:.3f} {unidade_var}/ano). Hipótese: região pode enfrentar **condições com amplitude térmica progressivamente maior**."
            elif slope < -0.05:
                tendencia_texto = f"**Tendência de Diminuição:** Os dados sugerem uma **diminuição** na {nome_var.lower()} na região {regiao_selecionada} ({slope:.3f} {unidade_var}/ano). Hipótese: região pode estar se tornando **com menor amplitude térmica**."
            else:
                tendencia_texto = f"**Tendência de Estabilidade:** A média anual da {nome_var.lower()} na região {regiao_selecionada} parece **relativamente estável** ({slope:.3f} {unidade_var}/ano). Hipótese: manutenção das condições médias, mas com atenção à variabilidade."

            print(tendencia_texto)

        else:
            print("Dados insuficientes (menos de 2 anos com dados válidos) para calcular uma tendência anual.")

        # --- HIPÓTESE 2: ANÁLISE DE VARIABILIDADE E EXTREMOS ---
        print("\n**Hipótese 2: Análise de Variabilidade Anual**")

        # Calcula o desvio absoluto médio de cada ano em relação à média histórica mensal
        desvios_abs_anuais = (df_valores_anuais.subtract(media_historica_mensal, axis=0)).abs().mean()
        desvios_abs_anuais = desvios_abs_anuais.dropna()

        if not desvios_abs_anuais.empty:
            ano_mais_atipico = desvios_abs_anuais.idxmax()
            maior_desvio = desvios_abs_anuais.max()

            print(f"Na Região **{regiao_selecionada}**, para a {nome_var}: ")
            print(f"- O ano de **{int(ano_mais_atipico)}** se destaca como o **mais atípico** (ou extremo), com as médias mensais se afastando em média **{maior_desvio:.2f} {unidade_var}** da média histórica do período.")

            print(f"**Hipótese de Variabilidade:** Se anos recentes consistentemente mostram maiores desvios, pode-se hipotetizar que o clima na região está se tornando **mais variável e propenso a extremos na {nome_var.lower()}**.")

            print("\n**Ranking de Anos por Desvio (Atipicidade na Média Mensal da Amplitude):**")
            desvios_df = pd.DataFrame(desvios_abs_anuais, columns=['Desvio Médio Absoluto'])
            print(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).to_string(float_format="%.2f"))
        else:
            print("Não há dados suficientes para realizar a análise de variabilidade anual.")
    else:
        print("Dados insuficientes para realizar a análise de tendência e variabilidade.")
