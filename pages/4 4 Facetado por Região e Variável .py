import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.cm import get_cmap

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos, calculando a amplitude térmica diária."""
    try:
        df = pd.read_csv(caminho)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho}' não foi encontrado. Por favor, verifique o caminho.")
        return pd.DataFrame()

    # Renomear colunas para facilitar o acesso, se existirem
    df.rename(columns={
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': 'Temp_Maxima',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': 'Temp_Minima'
    }, inplace=True)

    # Verifica se as colunas essenciais existem para calcular a amplitude
    if 'Temp_Maxima' in df.columns and 'Temp_Minima' in df.columns:
        df['Amplitude_Termica'] = df['Temp_Maxima'] - df['Temp_Minima']
    else:
        print("Aviso: Colunas de temperatura máxima e/ou mínima não encontradas. Não foi possível calcular 'Amplitude_Termica'.")
        return pd.DataFrame()

    # Converte colunas para numérico, tratando erros e removendo NaNs
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    df['Hora (UTC)'] = pd.to_numeric(df['Hora (UTC)'], errors='coerce') # Necessário para contar dias únicos
    df = df.dropna(subset=['Mês', 'Ano', 'Amplitude_Termica', 'Hora (UTC)']) # Garante que temos dados completos para a análise

    return df

# --- CARREGAMENTO DOS DADOS ---
df_unificado = carregar_dados(caminho_arquivo_unificado)

if df_unificado.empty:
    print("Não foi possível carregar ou processar os dados. Verifique o caminho do arquivo e as colunas de temperatura.")
else:
    if 'Amplitude_Termica' not in df_unificado.columns:
        print("Erro: 'Amplitude_Termica' não calculada. Verifique as colunas de temperatura no seu CSV.")
    else:
        # --- DEFINIÇÕES PARA ANÁLISE ---
        regiao_selecionada = 'SUDESTE' # Altere esta região conforme necessário
        limiar_amplitude_elevada = 10.0 # Define o limiar em °C para considerar amplitude "elevada"

        print(f"\n--- Análise de Dias com Amplitude Térmica Elevada ({limiar_amplitude_elevada}°C+) na Região {regiao_selecionada} ---")

        # --- FILTRAGEM DE DADOS ---
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada].copy()

        if df_regiao.empty:
            print(f"Não há dados para a região '{regiao_selecionada}' no arquivo fornecido.")
        else:
            # Identifica os dias com amplitude térmica elevada
            df_regiao['Amplitude_Elevada'] = df_regiao['Amplitude_Termica'] >= limiar_amplitude_elevada

            # Para contar os dias únicos com amplitude elevada, precisamos de uma data única para cada registro
            # Assumimos que cada linha representa uma leitura em um ponto do dia. Para contar "dias", precisamos de uma data
            # Se seu CSV tem uma coluna de data, use-a. Caso contrário, criamos uma combinação Ano-Mês-Dia.
            # O ideal seria ter uma coluna de 'Data' ou 'Dia' no seu CSV
            if 'DATA (YYYY-MM-DD)' in df_regiao.columns:
                df_regiao['Data_Unica'] = pd.to_datetime(df_regiao['DATA (YYYY-MM-DD)'])
            else:
                # Se não há coluna de DATA, tentamos criar uma para identificar dias únicos
                # Esta abordagem pode ser imperfeita se houver múltiplas leituras no mesmo dia sem uma coluna de data
                df_regiao['Data_Unica'] = pd.to_datetime(df_regiao['Ano'].astype(str) + '-' +
                                                         df_regiao['Mês'].astype(str) + '-' +
                                                         df_regiao.groupby(['Ano', 'Mês']).cumcount().add(1).astype(str), errors='coerce')
                df_regiao.dropna(subset=['Data_Unica'], inplace=True) # Remove datas inválidas criadas

            # Agrupa por Ano e Mês e conta os dias únicos que tiveram amplitude elevada
            # Primeiro, filtra apenas as entradas com amplitude elevada
            df_elevada = df_regiao[df_regiao['Amplitude_Elevada']].copy()

            # Em seguida, conta o número de dias únicos com amplitude elevada por mês e ano
            # Usamos .nunique() na Data_Unica para contar apenas uma vez por dia
            contagem_dias_elevada = df_elevada.groupby(['Ano', 'Mês'])['Data_Unica'].nunique().unstack(level=0)
            contagem_dias_elevada = contagem_dias_elevada.fillna(0) # Preenche meses sem dias elevados com 0

            # Garante que todos os meses de 1 a 12 estão presentes e em ordem
            contagem_dias_elevada = contagem_dias_elevada.reindex(range(1, 13)).fillna(0)

            anos_disponiveis = contagem_dias_elevada.columns.tolist()

            # --- VISUALIZAÇÃO: Número de Dias com Amplitude Elevada por Mês e Ano ---
            print(f"\nGerando gráfico de 'Número de Dias com Amplitude Térmica Diária Acima de {limiar_amplitude_elevada}°C'...")
            fig, ax = plt.subplots(figsize=(14, 7))

            cmap = get_cmap('viridis')
            cores_anos = {ano: cmap(i / (len(anos_disponiveis) - 1 if len(anos_disponiveis) > 1 else 1))
                          for i, ano in enumerate(anos_disponiveis)}

            for ano in anos_disponiveis:
                ax.plot(contagem_dias_elevada.index, contagem_dias_elevada[ano],
                        marker='o', linestyle='-', color=cores_anos.get(ano, 'gray'), label=str(int(ano)))

            ax.set_title(f'Número de Dias com Amplitude Térmica Diária $\\ge {limiar_amplitude_elevada}°C$ por Mês e Ano - {regiao_selecionada}', fontsize=16)
            ax.set_xlabel('Mês', fontsize=12)
            ax.set_ylabel(f'Número de Dias ($\ge {limiar_amplitude_elevada}°C$)', fontsize=12)
            ax.set_xticks(range(1, 13))
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(title='Ano', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()

            print("\n--- Interpretação dos Resultados ---")
            print(f"Este gráfico mostra a ocorrência de dias com amplitude térmica diária igual ou superior a **{limiar_amplitude_elevada}°C** ao longo dos meses e anos na região **{regiao_selecionada}**.")
            print("Picos na linha indicam meses e anos com maior frequência de dias com grandes variações de temperatura.")
            print("\n**Meses/Anos com Variações Mais Acentuadas (em termos de frequência de amplitudes elevadas):**")

            # Identificar o mês com maior média de dias elevados
            media_dias_elevados_por_mes = contagem_dias_elevada.mean(axis=1)
            mes_maior_media = media_dias_elevados_por_mes.idxmax()
            print(f"- O mês de **{int(mes_maior_media)}** (Média: {media_dias_elevados_por_mes.max():.1f} dias) historicamente apresenta a maior média de dias com amplitude térmica elevada.")

            # Identificar o ano com o maior número total de dias elevados
            total_dias_elevados_por_ano = contagem_dias_elevada.sum(axis=0)
            ano_maior_total = total_dias_elevados_por_ano.idxmax()
            print(f"- O ano de **{int(ano_maior_total)}** (Total: {total_dias_elevados_por_ano.max():.1f} dias) teve o maior número total de dias com amplitude térmica elevada no período analisado.")

            print("\n**Possíveis Hipóteses e Observações:**")
            print(f"- Se a linha para os anos mais recentes estiver consistentemente mais alta, isso pode sugerir uma tendência de **aumento na frequência de dias com amplitude térmica elevada**.")
            print("- Meses com maior número de dias com amplitude elevada podem indicar períodos de transição de estações ou menor nebulosidade, permitindo maior irradiação solar diurna e resfriamento noturno.")
            print(f"- A variação entre os anos para o mesmo mês pode indicar a **variabilidade climática** de um ano para outro, merecendo investigações mais aprofundadas (ex: influência de El Niño/La Niña).")
