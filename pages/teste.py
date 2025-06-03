import pandas as pd
from datetime import datetime

def analisar_frequencia_chuva_extrema_multianual(lista_arquivos_dados, nome_cidade, anos_analise=5, limiar_chuva_mm=50.0):
    """
    Analisa a frequência de eventos extremos de chuva para uma cidade,
    considerando dados de múltiplos arquivos (ex: um por ano).

    Args:
        lista_arquivos_dados (list): Lista de strings com os caminhos para os arquivos CSV.
        nome_cidade (str): Nome da cidade para análise.
        anos_analise (int): Número de anos recentes para analisar (usado para filtrar
                              os dados consolidados).
        limiar_chuva_mm (float): Limiar em mm para considerar um evento de chuva como extremo.

    Returns:
        None: Imprime a análise da frequência dos eventos.
    """
    if not lista_arquivos_dados:
        print("Erro: A lista de arquivos de dados está vazia.")
        return

    todos_os_dados = []

    print(f"Processando arquivos para a cidade: {nome_cidade}")
    for arquivo_csv in lista_arquivos_dados:
        try:
            # Tentar ler o CSV. Ajuste encoding e separador decimal se necessário.
            # O cabeçalho fornecido sugere que os nomes das colunas podem ter espaços e acentos.
            df_anual = pd.read_csv(
                arquivo_csv,
                decimal=',',       # Considera vírgula como separador decimal
                thousands='.',     # Considera ponto como separador de milhar (se houver)
                encoding='latin1', # Tente 'utf-8' ou 'iso-8859-1' se 'latin1' falhar
                na_values=['null', 'NULL', '', 'NA', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', 'N/A', 'NULL', 'NaN', 'nan']
            )
            print(f"Lido com sucesso: {arquivo_csv}. Colunas encontradas: {df_anual.columns.tolist()}")

            # Padronizar nomes das colunas importantes (ajuste se os nomes exatos variarem)
            coluna_precipitacao = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'
            coluna_data = 'Data' # Assumindo que existe uma coluna 'Data'

            if coluna_data not in df_anual.columns:
                print(f"AVISO: Coluna '{coluna_data}' não encontrada em {arquivo_csv}. Tentando inferir data de outra forma ou pulando arquivo.")
                # Você pode precisar adicionar lógica aqui para lidar com arquivos sem coluna 'Data'
                # ou se a data estiver em colunas separadas (Dia, Mes, Ano).
                # Por ora, vamos pular arquivos sem uma coluna de data clara.
                # Se 'Hora UTC' for relevante, precisará ser combinada com 'Data'.
                continue # Pula para o próximo arquivo se não houver coluna 'Data'


            if coluna_precipitacao not in df_anual.columns:
                print(f"AVISO: Coluna '{coluna_precipitacao}' não encontrada em {arquivo_csv}. Pulando este arquivo.")
                continue

            # Selecionar apenas as colunas necessárias para economizar memória
            df_selecionado = df_anual[[coluna_data, coluna_precipitacao]].copy()

            # Converter coluna de precipitação para numérico.
            # Erros na conversão viram NaN (Not a Number).
            df_selecionado.loc[:, coluna_precipitacao] = pd.to_numeric(
                df_selecionado[coluna_precipitacao], errors='coerce'
            )

            # Converter coluna 'Data' para datetime
            # Tenta formatos comuns. Se o seu formato for diferente, ajuste o 'format'.
            try:
                df_selecionado.loc[:, coluna_data] = pd.to_datetime(df_selecionado[coluna_data], errors='coerce', dayfirst=True)
            except Exception as e_dt:
                print(f"Não foi possível converter a coluna '{coluna_data}' para data em {arquivo_csv} com formato DD/MM/YYYY. Erro: {e_dt}. Tentando outros formatos...")
                try:
                    df_selecionado.loc[:, coluna_data] = pd.to_datetime(df_selecionado[coluna_data], errors='coerce') # Tenta inferir
                except Exception as e_dt2:
                    print(f"Falha ao converter data em {arquivo_csv} mesmo inferindo: {e_dt2}. Pulando este arquivo.")
                    continue


            # Remover linhas onde a data ou precipitação não puderam ser convertidas
            df_selecionado.dropna(subset=[coluna_data, coluna_precipitacao], inplace=True)

            todos_os_dados.append(df_selecionado)

        except FileNotFoundError:
            print(f"Erro: O arquivo '{arquivo_csv}' não foi encontrado.")
        except pd.errors.EmptyDataError:
            print(f"Aviso: O arquivo '{arquivo_csv}' está vazio.")
        except Exception as e:
            print(f"Ocorreu um erro ao processar o arquivo {arquivo_csv}: {e}")

    if not todos_os_dados:
        print(f"Nenhum dado válido foi carregado para {nome_cidade}. Encerrando análise.")
        return

    df_completo = pd.concat(todos_os_dados, ignore_index=True)
    df_completo.rename(columns={
        coluna_data: 'data',
        coluna_precipitacao: 'precipitacao_mm'
    }, inplace=True)

    print(f"\nTotal de registros carregados para {nome_cidade} após concatenação: {len(df_completo)}")
    if df_completo.empty:
        print("Nenhum dado para analisar após concatenação e limpeza.")
        return

    # Certificar que 'data' é datetime
    df_completo['data'] = pd.to_datetime(df_completo['data'], errors='coerce')
    df_completo.dropna(subset=['data'], inplace=True)


    # Filtrar dados para os últimos 'anos_analise' anos a partir da data mais recente nos dados
    data_mais_recente_nos_dados = df_completo['data'].max()
    data_inicio_analise = data_mais_recente_nos_dados - pd.DateOffset(years=anos_analise)

    df_recente = df_completo[df_completo['data'] >= data_inicio_analise].copy() # Usar .copy() para evitar SettingWithCopyWarning

    if df_recente.empty:
        print(f"Não há dados disponíveis para os últimos {anos_analise} anos (a partir de {data_inicio_analise.strftime('%Y-%m-%d')}).")
        return

    print(f"Analisando dados de {df_recente['data'].min().strftime('%Y-%m-%d')} até {df_recente['data'].max().strftime('%Y-%m-%d')}.")

    # Identificar eventos de chuva extrema
    # Usar .loc para atribuição segura para evitar SettingWithCopyWarning
    df_recente.loc[:, 'evento_extremo'] = df_recente['precipitacao_mm'] >= limiar_chuva_mm

    # Agrupar por ano e contar os eventos extremos
    df_recente.loc[:, 'ano'] = df_recente['data'].dt.year
    contagem_eventos_por_ano = df_recente[df_recente['evento_extremo']].groupby('ano').size().reindex(
        range(df_recente['ano'].min(), df_recente['ano'].max() + 1), fill_value=0
    )


    if contagem_eventos_por_ano.sum() == 0: # Verifica se houve algum evento extremo no período
        print(f"\nNenhum evento de chuva extrema (≥ {limiar_chuva_mm} mm) encontrado para {nome_cidade} nos últimos {anos_analise} anos ({data_inicio_analise.strftime('%Y')} a {data_mais_recente_nos_dados.strftime('%Y')}).")
        return

    print(f"\nFrequência de eventos de chuva extrema (≥ {limiar_chuva_mm} mm) em {nome_cidade} por ano:")
    print(contagem_eventos_por_ano)

    # Análise de tendência simples
    if len(contagem_eventos_por_ano) >= 2:
        anos_com_dados = contagem_eventos_por_ano[contagem_eventos_por_ano.index >= df_recente['ano'].min()] # Considerar apenas anos com dados efetivos
        if len(anos_com_dados) < 2:
            print("\nNão há dados suficientes de anos distintos com eventos para uma análise de tendência.")
            return

        # Verifica se há uma tendência linear de aumento (muito simplista)
        # Para uma análise robusta, seriam necessários testes estatísticos (ex: Mann-Kendall)
        diff_eventos = anos_com_dados.diff().dropna()
        if not diff_eventos.empty:
            if (diff_eventos > 0).all():
                print(f"\nA frequência de eventos extremos aumentou consistentemente ano a ano no período analisado.")
            elif (diff_eventos < 0).all():
                print(f"\nA frequência de eventos extremos diminuiu consistentemente ano a ano no período analisado.")
            elif anos_com_dados.iloc[-1] > anos_com_dados.iloc[0] and len(anos_com_dados) > 2 : # Se o último ano tem mais que o primeiro
                 # Média da primeira metade vs segunda metade
                meio = len(anos_com_dados) // 2
                media_primeira_metade = anos_com_dados.iloc[:meio].mean()
                media_segunda_metade = anos_com_dados.iloc[meio:].mean()
                if media_segunda_metade > media_primeira_metade:
                    print(f"\nA frequência média de eventos extremos parece ter aumentado na segunda metade do período analisado.")
                elif media_segunda_metade < media_primeira_metade:
                    print(f"\nA frequência média de eventos extremos parece ter diminuído na segunda metade do período analisado.")
                else:
                    print(f"\nA frequência média de eventos extremos parece ter permanecido estável entre as metades do período.")
            elif anos_com_dados.iloc[-1] == anos_com_dados.iloc[0] and len(anos_com_dados) > 1:
                 print(f"\nA frequência de eventos extremos no último ano analisado é igual à do primeiro, mas pode ter variado nos anos intermediários.")
            else:
                print(f"\nA tendência da frequência de eventos extremos é variável no período analisado.")
        else:
            print("\nNão há variação suficiente nos dados para uma análise de tendência simples (ex: apenas um ano com eventos).")

    elif len(contagem_eventos_por_ano) == 1:
        print("\nDados de apenas um ano com eventos extremos. Não é possível analisar tendência de aumento ou diminuição.")
    else:
        print("\nNão há dados suficientes para uma análise de tendência.")

# --- COMO USAR ---
# 1. Defina o nome da cidade
NOME_DA_CIDADE = "SUA_CIDADE_AQUI"  # <--- SUBSTITUA AQUI

# 2. Crie uma lista com os caminhos para os arquivos CSV da sua cidade.
#    Estes arquivos devem estar acessíveis para o script (ex: na mesma pasta ou caminho completo).
#    Se você clonou o repositório do GitHub e está rodando o script de dentro da pasta `CIADM1A`,
#    os caminhos podem ser algo como:
#    '2023/arquivo_da_sua_cidade_2023.csv',
#    '2024/arquivo_da_sua_cidade_2024.csv',
#    etc.
#    Para os últimos 5 anos (considerando que estamos em 2025), você precisaria dos dados de
#    ~metade de 2020, 2021, 2022, 2023, 2024 e talvez a parte de 2025 já disponível.
#
#    EXEMPLO (VOCÊ PRECISA AJUSTAR ISTO CONFORME SEUS ARQUIVOS):
#    lista_arquivos_dados = [
#        './CIADM1A/2020/NOME_DO_ARQUIVO_DA_CIDADE_2020.csv', # Exemplo de estrutura
#        './CIADM1A/2021/NOME_DO_ARQUIVO_DA_CIDADE_2021.csv',
#        './CIADM1A/2022/NOME_DO_ARQUIVO_DA_CIDADE_2022.csv',
#        './CIADM1A/2023/NOME_DO_ARQUIVO_DA_CIDADE_2023.csv',
#        './CIADM1A/2024/NOME_DO_ARQUIVO_DA_CIDADE_2024.csv',
#        # './CIADM1A/2025/NOME_DO_ARQUIVO_DA_CIDADE_2025.csv' # Se já houver dados de 2025
#    ]
#
#    COMO VOCÊ NÃO ESPECIFICOU OS NOMES DOS ARQUIVOS, DEIXAREI UMA LISTA VAZIA.
#    VOCÊ PRECISA PREENCHER ESSA LISTA CORRETAMENTE.
lista_arquivos_dados = [] # <--- PREENCHA AQUI COM OS CAMINHOS DOS SEUS ARQUIVOS

if NOME_DA_CIDADE == "SUA_CIDADE_AQUI" or not lista_arquivos_dados:
    print("---------------------------------------------------------------------------")
    print("ATENÇÃO: Configure as variáveis 'NOME_DA_CIDADE' e 'lista_arquivos_dados'")
    print("         no script antes de executá-lo.")
    print("         A 'lista_arquivos_dados' deve conter os caminhos para os arquivos CSV")
    print("         da cidade desejada, cobrindo os últimos 5 anos.")
    print("---------------------------------------------------------------------------")
else:
    analisar_frequencia_chuva_extrema_multianual(lista_arquivos_dados, NOME_DA_CIDADE)
