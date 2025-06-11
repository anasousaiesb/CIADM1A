import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.cm import get_cmap

# Caminho relativo ao arquivo CSV
# Certifique-se de que este arquivo existe e está no caminho correto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    try:
        df = pd.read_csv(caminho)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho}' não foi encontrado. Por favor, verifique o caminho.")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

    # Converte colunas essenciais para numérico, tratando erros e removendo NaNs
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df = df.dropna(subset=['Mês', 'Ano']) # Remove linhas onde Mês ou Ano não são válidos

    # Verifica se a coluna de precipitação existe
    if 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' not in df.columns:
        print("Erro: A coluna 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' não foi encontrada no arquivo CSV. Verifique o cabeçalho.")
        return pd.DataFrame() # Retorna um DataFrame vazio se a coluna essencial estiver faltando

    return df

# --- CARREGAMENTO DOS DADOS ---
df_unificado = carregar_dados(caminho_arquivo_unificado)

if df_unificado.empty:
    print("Não foi possível carregar ou processar os dados. Verifique o caminho do arquivo e as colunas necessárias.")
else:
    # --- DEFINIÇÕES PARA ANÁLISE ---
    regiao_selecionada = 'NORDESTE' # Você pode mudar esta região para testar outras
    coluna_precipitacao = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'

    print(f"\n--- Análise do Mês de Maior Precipitação na Região {regiao_selecionada} ---")

    # --- FILTRAGEM DE DADOS ---
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada].copy()

    if df_regiao.empty:
        print(f"Não há dados para a região '{regiao_selecionada}' no arquivo fornecido.")
    else:
        anos_disponiveis = sorted(df_regiao['Ano'].unique())

        # Encontra o mês de maior precipitação e o valor dessa precipitação para cada ano
        dados_max_precipitacao = []
        for ano in anos_disponiveis:
            df_ano = df_regiao[df_regiao['Ano'] == ano]
            if not df_ano.empty and not df_ano[coluna_precipitacao].isnull().all(): # Garante que há dados de precipitação para o ano
                idx_max_precip = df_ano[coluna_precipitacao].idxmax()
                mes_max_precip = int(df_ano.loc[idx_max_precip]['Mês'])
                valor_max_precip = df_ano.loc[idx_max_precip][coluna_precipitacao]
                dados_max_precipitacao.append({
                    'Ano': ano,
                    'Mês_Maior_Precipitacao': mes_max_precip,
                    'Valor_Maior_Precipitacao_mm': valor_max_precip
                })
            else:
                print(f"Aviso: Sem dados de precipitação para o ano {int(ano)} na região {regiao_selecionada}. Ignorando este ano na análise.")

        df_resumo_precip = pd.DataFrame(dados_max_precipitacao)

        if df_resumo_precip.empty:
            print("Não há dados suficientes de precipitação para realizar a análise.")
        else:
            # --- VISUALIZAÇÃO 1: Mês de Maior Precipitação por Ano ---
            print("\nGerando gráfico do 'Mês de Maior Precipitação por Ano'...")
            fig1, ax1 = plt.subplots(figsize=(10, 6))

            ax1.plot(df_resumo_precip['Ano'], df_resumo_precip['Mês_Maior_Precipitacao'],
                     marker='o', linestyle='-', color='skyblue', label='Mês de Maior Precipitação')

            ax1.set_title(f'Mês de Maior Precipitação Total Anual - Região {regiao_selecionada}', fontsize=16)
            ax1.set_xlabel('Ano', fontsize=12)
            ax1.set_ylabel('Mês', fontsize=12)
            ax1.set_yticks(range(1, 13)) # Mostra todos os meses no eixo Y
            ax1.set_xticks(df_resumo_precip['Ano']) # Define ticks para cada ano disponível
            ax1.grid(True, linestyle='--', alpha=0.6)
            ax1.legend()
            plt.tight_layout()
            plt.show() # Mostra o primeiro gráfico

            # --- VISUALIZAÇÃO 2: Valor da Maior Precipitação Anual por Ano ---
            print("\nGerando gráfico do 'Valor da Maior Precipitação Anual por Ano'...")
            fig2, ax2 = plt.subplots(figsize=(10, 6))

            ax2.plot(df_resumo_precip['Ano'], df_resumo_precip['Valor_Maior_Precipitacao_mm'],
                     marker='o', linestyle='-', color='lightcoral', label='Precipitação Máxima Anual (mm)')

            ax2.set_title(f'Valor da Maior Precipitação Total Anual - Região {regiao_selecionada}', fontsize=16)
            ax2.set_xlabel('Ano', fontsize=12)
            ax2.set_ylabel('Precipitação (mm)', fontsize=12)
            ax2.set_xticks(df_resumo_precip['Ano']) # Define ticks para cada ano disponível
            ax2.grid(True, linestyle='--', alpha=0.6)
            ax2.legend()
            plt.tight_layout()
            plt.show() # Mostra o segundo gráfico

            print("\n--- Interpretação dos Resultados ---")
            print(f"**Análise para a Região: {regiao_selecionada}**")
            print("-----------------------------------")

            # Análise do Mês de Maior Precipitação
            print("\n**Variação do Mês de Maior Precipitação:**")
            if df_resumo_precip['Mês_Maior_Precipitacao'].nunique() == 1:
                print(f"O mês de maior precipitação foi consistentemente o Mês **{int(df_resumo_precip['Mês_Maior_Precipitacao'].iloc[0])}** em todos os anos analisados.")
            else:
                meses_ocorrencia = df_resumo_precip['Mês_Maior_Precipitacao'].value_counts().index.tolist()
                print(f"O mês de maior precipitação **variou** entre os anos. Os meses que mais se destacaram como os mais chuvosos foram: {meses_ocorrencia}.")
                print(f"Mês mais frequente como o mais chuvoso: Mês **{int(df_resumo_precip['Mês_Maior_Precipitacao'].mode()[0])}**.")

            # Análise da Variação Interanual da Precipitação Máxima
            print("\n**Variação Interanual da Precipitação Máxima:**")
            if len(df_resumo_precip) > 1:
                min_valor = df_resumo_precip['Valor_Maior_Precipitacao_mm'].min()
                max_valor = df_resumo_precip['Valor_Maior_Precipitacao_mm'].max()
                ano_min = df_resumo_precip.loc[df_resumo_precip['Valor_Maior_Precipitacao_mm'].idxmin()]['Ano']
                ano_max = df_resumo_precip.loc[df_resumo_precip['Valor_Maior_Precipitacao_mm'].idxmax()]['Ano']

                print(f"- A precipitação total máxima anual variou de **{min_valor:.2f} mm** (no ano {int(ano_min)}) a **{max_valor:.2f} mm** (no ano {int(ano_max)}) no período.")
                print(f"- Esta variação interanual pode indicar anos de chuva excepcionalmente intensa ou, inversamente, anos onde o pico de precipitação foi menor.")
                print("- Observe no segundo gráfico se há uma tendência de aumento ou diminuição no valor da precipitação máxima ao longo dos anos.")
            else:
                print("Dados insuficientes para analisar a variação interanual da precipitação máxima.")

            print("\nEssas análises são importantes para o planejamento de recursos hídricos e para entender a sazonalidade e a variabilidade climática da região.")
