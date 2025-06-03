import streamlit as st
import pandas as pd
from datetime import datetime
import io # Importado anteriormente, mas não usado diretamente nesta versão
import requests # Para baixar os arquivos do GitHub

# --- Configurações para a Análise de Eventos Extremos ---
# Você pode alterar NOME_CIDADE_DISPLAY e CODIGO_ESTACAO para a cidade de interesse
NOME_CIDADE_DISPLAY = "Brazlândia (DF)"
CODIGO_ESTACAO = "A042" # Código da estação INMET para Brazlândia
# Para "últimos 5 anos" e considerando que estamos em meados de 2025, pegaremos os anos completos anteriores.
# Se 2024 ainda não estiver completo ou disponível, a análise se ajustará aos anos encontrados.
ANOS_PARA_ANALISAR = [2020, 2021, 2022, 2023, 2024]

GITHUB_USER = "anasousaiesb"
GITHUB_REPO = "CIADM1A"
GITHUB_BRANCH = "main" # ou 'master', dependendo do repositório
BASE_PATH_IN_REPO = "CIADM1A" # Pasta raiz dos dados dentro do repositório

# Nomes das colunas como nos arquivos brutos do INMET
COLUNA_PRECIPITACAO_NOME_ORIGINAL = 'PRECIPITACAO TOTAL, HORARIO (mm)' # Ou o nome correto no seu CSV
COLUNA_DATA_NOME_ORIGINAL = 'Data'
COLUNA_HORA_NOME_ORIGINAL = 'Hora UTC' # Geralmente 'HORA UTC' ou 'Hora (UTC)'

def construir_url_arquivo(ano, codigo_estacao_local, nome_cidade_arquivo):
    """Constrói a URL para o arquivo de um ano específico."""
    # Exemplo de nome: INMET_CO_DF_A042_BRAZLANDIA_01-01-2020_A_31-12-2020.CSV
    # Ajuste o 'nome_cidade_arquivo' para corresponder ao padrão no seu repositório
    nome_arquivo = f"INMET_CO_DF_{codigo_estacao_local}_{nome_cidade_arquivo.upper()}_01-01-{ano}_A_31-12-{ano}.CSV"
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{BASE_PATH_IN_REPO}/{ano}/{nome_arquivo}"
    return url

def processar_dados_inmet_para_extremos(df_bruto, nome_arquivo_log):
    """Processa o DataFrame bruto do INMET para o formato necessário para análise de extremos."""
    mensagens_processamento = []
    df_selecionado = None

    colunas_necessarias = [COLUNA_DATA_NOME_ORIGINAL, COLUNA_HORA_NOME_ORIGINAL, COLUNA_PRECIPITACAO_NOME_ORIGINAL]
    colunas_presentes = [col for col in colunas_necessarias if col in df_bruto.columns]

    if len(colunas_presentes) != len(colunas_necessarias):
        colunas_faltantes = list(set(colunas_necessarias) - set(colunas_presentes))
        mensagens_processamento.append(f"AVISO ({nome_arquivo_log}): Colunas essenciais faltando: {', '.join(colunas_faltantes)}. Pulando este arquivo.")
        return None, mensagens_processamento

    try:
        df_processado = df_bruto[colunas_necessarias].copy()
        df_processado.loc[:, COLUNA_PRECIPITACAO_NOME_ORIGINAL] = pd.to_numeric(
            df_processado[COLUNA_PRECIPITACAO_NOME_ORIGINAL], errors='coerce'
        )
        
        # Tratar a coluna de hora, que geralmente é 'HHMM'
        df_processado.loc[:, 'hora_str'] = df_processado[COLUNA_HORA_NOME_ORIGINAL].astype(str).str.zfill(4).str.slice(0, 2) + ":00:00"

        # Tentar formatos de data
        try:
            df_processado.loc[:, 'datetime_completo'] = pd.to_datetime(
                df_processado[COLUNA_DATA_NOME_ORIGINAL] + ' ' + df_processado['hora_str'],
                format='%Y/%m/%d %H:%M:%S', errors='coerce' # Formato AAAA/MM/DD
            )
            if df_processado['datetime_completo'].isnull().all():
                df_processado.loc[:, 'datetime_completo'] = pd.to_datetime(
                    df_processado[COLUNA_DATA_NOME_ORIGINAL] + ' ' + df_processado['hora_str'],
                    format='%d/%m/%Y %H:%M:%S', errors='coerce' # Formato DD/MM/AAAA
                )
        except Exception as e_dt:
            mensagens_processamento.append(f"AVISO ({nome_arquivo_log}): Falha ao converter data/hora: {e_dt}. Verifique os formatos.")
            return None, mensagens_processamento
        
        df_selecionado = df_processado[['datetime_completo', COLUNA_PRECIPITACAO_NOME_ORIGINAL]].copy()
        df_selecionado.rename(columns={
            'datetime_completo': 'data',
            COLUNA_PRECIPITACAO_NOME_ORIGINAL: 'precipitacao_mm'
        }, inplace=True)
        df_selecionado.dropna(subset=['data', 'precipitacao_mm'], inplace=True)
        
    except Exception as e:
        mensagens_processamento.append(f"ERRO ({nome_arquivo_log}): Erro no processamento detalhado: {e}")
        return None, mensagens_processamento
    
    return df_selecionado, mensagens_processamento

def analisar_eventos_extremos_chuva(anos_lista, nome_cidade_display, codigo_estacao_local, nome_cidade_arquivo, limiar_chuva_mm):
    """
    Função principal para carregar dados, identificar eventos extremos e analisar tendência.
    """
    resultados = {
        "mensagens_status": [],
        "contagem_eventos_df": None,
        "mensagem_tendencia": "Nenhuma análise de tendência realizada ainda.",
        "periodo_analisado_str": "",
        "anos_com_dados": []
    }
    
    todos_os_dados_anuais = []
    
    for ano in anos_lista:
        url = construir_url_arquivo(ano, codigo_estacao_local, nome_cidade_arquivo)
        resultados["mensagens_status"].append(f"Tentando carregar dados para {ano} de: {url}")
        
        try:
            # Usar requests para melhor tratamento de erros HTTP
            response = requests.get(url)
            response.raise_for_status() # Levanta um erro para códigos HTTP 4xx/5xx
            
            # skiprows=8 é comum para INMET, ajuste se necessário
            df_bruto_anual = pd.read_csv(
                io.StringIO(response.text), # Ler do texto da resposta
                decimal=',',
                encoding='latin1', 
                na_values=['null', 'NULL', '', 'NA', '#N/A', 'NA ', '-9999', '-9999.0'],
                skiprows=8 
            )
            
            df_processado_anual, mensagens_proc = processar_dados_inmet_para_extremos(df_bruto_anual, f"Ano {ano}")
            resultados["mensagens_status"].extend(mensagens_proc)

            if df_processado_anual is not None and not df_processado_anual.empty:
                todos_os_dados_anuais.append(df_processado_anual)
                resultados["anos_com_dados"].append(ano)
                resultados["mensagens_status"].append(f"Dados para o ano {ano} carregados e processados com sucesso ({len(df_processado_anual)} registros).")
            else:
                resultados["mensagens_status"].append(f"Nenhum dado válido processado para o ano {ano}.")

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                 resultados["mensagens_status"].append(f"AVISO: Arquivo para o ano {ano} não encontrado (404). URL: {url}")
            else:
                 resultados["mensagens_status"].append(f"AVISO: Erro HTTP ao buscar arquivo para {ano}. URL: {url}. Erro: {http_err}")
        except Exception as e:
            resultados["mensagens_status"].append(f"AVISO: Não foi possível carregar ou processar o arquivo para o ano {ano}. URL: {url}. Erro: {e}")

    if not todos_os_dados_anuais:
        resultados["mensagens_status"].append(f"Nenhum dado válido foi carregado para {nome_cidade_display} para os anos especificados.")
        resultados["mensagem_tendencia"] = "Nenhum dado encontrado para análise."
        return resultados

    df_completo = pd.concat(todos_os_dados_anuais, ignore_index=True)
    df_completo.sort_values(by='data', inplace=True)
    
    if df_completo.empty:
        resultados["mensagem_tendencia"] = "Nenhum dado válido após concatenação."
        return resultados

    resultados["mensagens_status"].append(f"Total de {len(df_completo)} registros horários carregados dos anos: {', '.join(map(str, sorted(resultados['anos_com_dados'])))}.")
    
    min_date_str = df_completo['data'].min().strftime('%Y-%m-%d %H:%M')
    max_date_str = df_completo['data'].max().strftime('%Y-%m-%d %H:%M')
    resultados["periodo_analisado_str"] = f"Analisando dados horários de {min_date_str} até {max_date_str}."
    
    # Identificar eventos extremos (precipitação horária >= limiar)
    df_completo['evento_extremo'] = df_completo['precipitacao_mm'] >= limiar_chuva_mm
    df_completo['ano_evento'] = df_completo['data'].dt.year
    
    anos_unicos_dados = sorted(df_completo['ano_evento'].unique())
    if not anos_unicos_dados:
        resultados["mensagem_tendencia"] = "Nenhum ano encontrado nos dados processados."
        return resultados

    contagem_eventos_por_ano = df_completo[df_completo['evento_extremo']].groupby('ano_evento').size().reindex(
        range(min(anos_unicos_dados), max(anos_unicos_dados) + 1), fill_value=0
    )
    contagem_eventos_por_ano = contagem_eventos_por_ano[contagem_eventos_por_ano.index.isin(resultados["anos_com_dados"])]
    
    resultados["contagem_eventos_df"] = contagem_eventos_por_ano.reset_index().rename(
        columns={'ano_evento': 'Ano', 0: f'Eventos (≥{limiar_chuva_mm}mm/hora)'}
    )

    if contagem_eventos_por_ano.sum() == 0:
        resultados["mensagem_tendencia"] = f"Nenhum evento de chuva extrema (≥ {limiar_chuva_mm} mm/hora) encontrado para {nome_cidade_display} nos anos com dados."
        return resultados
    
    num_anos_validos = len(contagem_eventos_por_ano)
    if num_anos_validos >= 2:
        # Lógica de tendência simplificada (comparando primeira e segunda metade se houver dados suficientes)
        if num_anos_validos >= 3: # Pelo menos 3 pontos para dividir
            meio = num_anos_validos // 2
            media_primeira_metade = contagem_eventos_por_ano.iloc[:meio].mean()
            media_segunda_metade = contagem_eventos_por_ano.iloc[meio:].mean()
            
            if media_segunda_metade > media_primeira_metade:
                resultados["mensagem_tendencia"] = (f"A frequência média de eventos extremos horários parece ter **aumentado** na segunda metade do período "
                                                  f"({media_segunda_metade:.1f} eventos/ano) em comparação com a primeira metade ({media_primeira_metade:.1f} eventos/ano).")
            elif media_segunda_metade < media_primeira_metade:
                resultados["mensagem_tendencia"] = (f"A frequência média de eventos extremos horários parece ter **diminuído** na segunda metade do período "
                                                  f"({media_segunda_metade:.1f} eventos/ano) em comparação com a primeira metade ({media_primeira_metade:.1f} eventos/ano).")
            else:
                resultados["mensagem_tendencia"] = (f"A frequência média de eventos extremos horários permaneceu **estável** ({media_primeira_metade:.1f} eventos/ano) "
                                                  f"entre a primeira e a segunda metade do período.")
        elif num_anos_validos == 2:
            if contagem_eventos_por_ano.iloc[1] > contagem_eventos_por_ano.iloc[0]:
                resultados["mensagem_tendencia"] = "A frequência de eventos extremos horários aumentou do primeiro para o segundo ano analisado."
            elif contagem_eventos_por_ano.iloc[1] < contagem_eventos_por_ano.iloc[0]:
                resultados["mensagem_tendencia"] = "A frequência de eventos extremos horários diminuiu do primeiro para o segundo ano analisado."
            else:
                resultados["mensagem_tendencia"] = "A frequência de eventos extremos horários permaneceu a mesma entre os dois anos analisados."
    elif num_anos_validos == 1:
        resultados["mensagem_tendencia"] = "Dados de apenas um ano disponíveis. Não é possível determinar uma tendência de aumento ou diminuição na frequência de eventos."
    
    return resultados

# --- Interface Streamlit ---
st.set_page_config(layout="wide", page_title=f"Eventos Extremos de Chuva - {NOME_CIDADE_DISPLAY}")
st.title(f"🌧️ Frequência de Eventos Extremos de Chuva em {NOME_CIDADE_DISPLAY}")
st.markdown(f"Análise da frequência de precipitação horária ≥ 50 mm nos últimos 5 anos ({', '.join(map(str, ANOS_PARA_ANALISAR))}).")
st.markdown(f"Fonte dos dados: Estação INMET `{CODIGO_ESTACAO}` via GitHub (`{GITHUB_USER}/{GITHUB_REPO}`).")
st.markdown("---")

# Parâmetros (apenas o limiar é interativo aqui, cidade e anos são fixos pela configuração)
st.sidebar.header("Parâmetros da Análise")
st.sidebar.info(f"Cidade: {NOME_CIDADE_DISPLAY} (Estação {CODIGO_ESTACAO})")
st.sidebar.info(f"Anos Alvo: {', '.join(map(str, ANOS_PARA_ANALISAR))}")
limiar_chuva_mm_input = st.sidebar.number_input("Limiar de chuva extrema (mm/hora):", min_value=10.0, value=50.0, step=5.0, format="%.1f")

# Layout
col_info, col_grafico = st.columns([1, 2])

with col_info:
    if st.button(f"📊 Analisar {NOME_CIDADE_DISPLAY}", type="primary", use_container_width=True):
        with st.spinner(f"Buscando e analisando dados para {NOME_CIDADE_DISPLAY}..."):
            # O nome da cidade no arquivo pode ser diferente do nome de display (ex: BRAZLANDIA vs Brazlândia (DF))
            # Ajuste 'nome_cidade_arquivo' conforme o padrão dos seus arquivos CSV.
            nome_cidade_para_arquivo = "BRAZLANDIA" 
            
            st.session_state.resultados_extremos = analisar_eventos_extremos_chuva(
                ANOS_PARA_ANALISAR,
                NOME_CIDADE_DISPLAY,
                CODIGO_ESTACAO,
                nome_cidade_para_arquivo, # Nome da cidade como está no nome do arquivo
                limiar_chuva_mm_input
            )
    
    if 'resultados_extremos' in st.session_state:
        res = st.session_state.resultados_extremos
        st.subheader("Resumo da Análise")
        if res["anos_com_dados"]:
            st.write(f"**Anos com dados processados:** {', '.join(map(str, sorted(res['anos_com_dados'])))}")
        else:
            st.warning("Nenhum dado encontrado para os anos configurados.")
        
        st.markdown(f"**Pergunta:** A frequência de eventos de chuva ≥ {limiar_chuva_mm_input}mm/hora aumentou em {NOME_CIDADE_DISPLAY} nos últimos 5 anos?")
        if res["mensagem_tendencia"]:
            st.info(f"**Conclusão (com base nos dados disponíveis):** {res['mensagem_tendencia']}")
        else:
            st.warning("Não foi possível concluir a análise de tendência.")

        if res["periodo_analisado_str"]:
            st.caption(res["periodo_analisado_str"])
        
        with st.expander("Ver Logs de Processamento"):
            for msg in res["mensagens_status"]:
                if "ERRO:" in msg:
                    st.error(msg)
                elif "AVISO:" in msg or "não encontrado" in msg:
                    st.warning(msg)
                else:
                    st.text(msg)
    else:
        st.info("Clique no botão 'Analisar' para iniciar.")

with col_grafico:
    if 'resultados_extremos' in st.session_state and st.session_state.resultados_extremos["contagem_eventos_df"] is not None:
        df_plot = st.session_state.resultados_extremos["contagem_eventos_df"]
        if not df_plot.empty:
            st.subheader(f"Número de Eventos de Chuva Extrema (≥{limiar_chuva_mm_input}mm/hora) por Ano")
            
            # Tabela
            st.dataframe(df_plot.style.format({"Ano": "{:.0f}", f"Eventos (≥{limiar_chuva_mm_input}mm/hora)": "{:.0f}"}), use_container_width=True)

            # Gráfico de Barras
            df_grafico = df_plot.set_index('Ano')
            st.bar_chart(df_grafico[f"Eventos (≥{limiar_chuva_mm_input}mm/hora)"])
        else:
            st.write("Nenhum evento extremo encontrado para plotar com os critérios atuais.")

st.sidebar.markdown("---")
st.sidebar.caption("Análise de frequência de eventos extremos de chuva horária.")
