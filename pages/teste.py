import streamlit as st
import pandas as pd
from datetime import datetime

# Funções auxiliares para manter o código da função principal mais limpo
def processar_arquivo_individual(uploaded_file, nome_arquivo, col_data, col_precipitacao):
    """Processa um único arquivo CSV carregado."""
    mensagens_processamento = []
    df_selecionado = None
    try:
        df_anual = pd.read_csv(
            uploaded_file,
            decimal=',',
            thousands='.',
            encoding='latin1',
            na_values=['null', 'NULL', '', 'NA', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', 'N/A', 'NULL', 'NaN', 'nan']
        )
        mensagens_processamento.append(f"Lido com sucesso: {nome_arquivo}. Colunas encontradas: {df_anual.columns.tolist()}")

        if col_data not in df_anual.columns:
            mensagens_processamento.append(f"AVISO: Coluna '{col_data}' não encontrada em {nome_arquivo}.")
            return None, mensagens_processamento
        if col_precipitacao not in df_anual.columns:
            mensagens_processamento.append(f"AVISO: Coluna '{col_precipitacao}' não encontrada em {nome_arquivo}.")
            return None, mensagens_processamento

        df_selecionado = df_anual[[col_data, col_precipitacao]].copy()
        df_selecionado.loc[:, col_precipitacao] = pd.to_numeric(df_selecionado[col_precipitacao], errors='coerce')

        try:
            df_selecionado.loc[:, col_data] = pd.to_datetime(df_selecionado[col_data], errors='coerce', dayfirst=True)
        except Exception:
            try:
                df_selecionado.loc[:, col_data] = pd.to_datetime(df_selecionado[col_data], errors='coerce')
            except Exception as e_dt2:
                mensagens_processamento.append(f"Falha ao converter data em {nome_arquivo}: {e_dt2}. Pulando este arquivo.")
                return None, mensagens_processamento
        
        df_selecionado.dropna(subset=[col_data, col_precipitacao], inplace=True)
        
    except pd.errors.EmptyDataError:
        mensagens_processamento.append(f"Aviso: O arquivo '{nome_arquivo}' está vazio.")
    except Exception as e:
        mensagens_processamento.append(f"Ocorreu um erro ao processar o arquivo {nome_arquivo}: {e}")
    
    return df_selecionado, mensagens_processamento

def analisar_frequencia_chuva_streamlit(lista_arquivos_carregados, nome_cidade, anos_analise, limiar_chuva_mm):
    """
    Analisa a frequência de eventos extremos de chuva para Streamlit.
    Retorna um dicionário com resultados e mensagens.
    """
    resultados = {
        "mensagens_status": [],
        "contagem_eventos_df": None,
        "grafico_eventos": None, # Para o gráfico de barras
        "mensagem_tendencia": "",
        "periodo_analisado_str": ""
    }
    
    if not lista_arquivos_carregados:
        resultados["mensagens_status"].append("Erro: Nenhum arquivo foi carregado.")
        return resultados

    todos_os_dados = []
    coluna_precipitacao_nome_original = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'
    coluna_data_nome_original = 'Data' # Assumindo que existe uma coluna 'Data'

    resultados["mensagens_status"].append(f"Processando arquivos para a cidade: {nome_cidade}")

    for uploaded_file in lista_arquivos_carregados:
        df_processado, mensagens_proc = processar_arquivo_individual(
            uploaded_file, 
            uploaded_file.name, 
            coluna_data_nome_original, 
            coluna_precipitacao_nome_original
        )
        resultados["mensagens_status"].extend(mensagens_proc)
        if df_processado is not None and not df_processado.empty:
            todos_os_dados.append(df_processado)

    if not todos_os_dados:
        resultados["mensagens_status"].append(f"Nenhum dado válido foi carregado para {nome_cidade}. Encerrando análise.")
        return resultados

    df_completo = pd.concat(todos_os_dados, ignore_index=True)
    df_completo.rename(columns={
        coluna_data_nome_original: 'data',
        coluna_precipitacao_nome_original: 'precipitacao_mm'
    }, inplace=True)

    resultados["mensagens_status"].append(f"Total de registros carregados para {nome_cidade} após concatenação: {len(df_completo)}")
    if df_completo.empty:
        resultados["mensagens_status"].append("Nenhum dado para analisar após concatenação e limpeza.")
        return resultados

    df_completo['data'] = pd.to_datetime(df_completo['data'], errors='coerce')
    df_completo.dropna(subset=['data'], inplace=True)
    if df_completo.empty:
        resultados["mensagens_status"].append("Nenhum dado com datas válidas encontrado.")
        return resultados

    data_mais_recente_nos_dados = df_completo['data'].max()
    data_inicio_analise = data_mais_recente_nos_dados - pd.DateOffset(years=anos_analise)
    
    df_recente = df_completo[df_completo['data'] >= data_inicio_analise].copy()

    if df_recente.empty:
        resultados["mensagens_status"].append(f"Não há dados disponíveis para os últimos {anos_analise} anos (a partir de {data_inicio_analise.strftime('%Y-%m-%d')}).")
        return resultados

    resultados["periodo_analisado_str"] = f"Analisando dados de {df_recente['data'].min().strftime('%Y-%m-%d')} até {df_recente['data'].max().strftime('%Y-%m-%d')}."
    resultados["mensagens_status"].append(resultados["periodo_analisado_str"])
    
    df_recente.loc[:, 'evento_extremo'] = df_recente['precipitacao_mm'] >= limiar_chuva_mm
    df_recente.loc[:, 'ano'] = df_recente['data'].dt.year
    
    contagem_eventos_por_ano = df_recente[df_recente['evento_extremo']].groupby('ano').size().reindex(
        range(df_recente['ano'].min(), df_recente['ano'].max() + 1), fill_value=0
    )
    resultados["contagem_eventos_df"] = contagem_eventos_por_ano.reset_index(name='Numero de Eventos Extremos')


    if contagem_eventos_por_ano.sum() == 0:
        resultados["mensagem_tendencia"] = f"Nenhum evento de chuva extrema (≥ {limiar_chuva_mm} mm) encontrado para {nome_cidade} nos últimos {anos_analise} anos ({data_inicio_analise.strftime('%Y')} a {data_mais_recente_nos_dados.strftime('%Y')})."
        return resultados
    
    # Análise de tendência simples
    if len(contagem_eventos_por_ano) >= 2:
        anos_com_dados = contagem_eventos_por_ano[contagem_eventos_por_ano.index >= df_recente['ano'].min()]
        if len(anos_com_dados) < 2:
            resultados["mensagem_tendencia"] = "Não há dados suficientes de anos distintos com eventos para uma análise de tendência."
        else:
            diff_eventos = anos_com_dados.diff().dropna()
            if not diff_eventos.empty:
                if (diff_eventos > 0).all():
                    resultados["mensagem_tendencia"] = "A frequência de eventos extremos aumentou consistentemente ano a ano no período analisado."
                elif (diff_eventos < 0).all():
                    resultados["mensagem_tendencia"] = "A frequência de eventos extremos diminuiu consistentemente ano a ano no período analisado."
                elif anos_com_dados.iloc[-1] > anos_com_dados.iloc[0] and len(anos_com_dados) > 2:
                    meio = len(anos_com_dados) // 2
                    media_primeira_metade = anos_com_dados.iloc[:meio].mean()
                    media_segunda_metade = anos_com_dados.iloc[meio:].mean()
                    if media_segunda_metade > media_primeira_metade:
                        resultados["mensagem_tendencia"] = "A frequência média de eventos extremos parece ter aumentado na segunda metade do período analisado."
                    elif media_segunda_metade < media_primeira_metade:
                        resultados["mensagem_tendencia"] = "A frequência média de eventos extremos parece ter diminuído na segunda metade do período analisado."
                    else:
                        resultados["mensagem_tendencia"] = "A frequência média de eventos extremos parece ter permanecido estável entre as metades do período."
                elif anos_com_dados.iloc[-1] == anos_com_dados.iloc[0] and len(anos_com_dados) > 1:
                    resultados["mensagem_tendencia"] = "A frequência de eventos extremos no último ano analisado é igual à do primeiro, mas pode ter variado nos anos intermediários."
                else:
                    resultados["mensagem_tendencia"] = "A tendência da frequência de eventos extremos é variável no período analisado."
            else:
                resultados["mensagem_tendencia"] = "Não há variação suficiente nos dados para uma análise de tendência simples (ex: apenas um ano com eventos)."
    elif len(contagem_eventos_por_ano) == 1:
        resultados["mensagem_tendencia"] = "Dados de apenas um ano com eventos extremos. Não é possível analisar tendência de aumento ou diminuição."
    else:
        resultados["mensagem_tendencia"] = "Não há dados suficientes para uma análise de tendência."
        
    return resultados

# --- Interface Streamlit ---
st.set_page_config(layout="wide", page_title="Análise de Chuvas Extremas")
st.title("🌧️ Análise de Frequência de Chuvas Extremas")
st.markdown("Carregue seus arquivos CSV de dados meteorológicos para analisar a frequência de eventos de chuva extrema.")

# Inputs na barra lateral
st.sidebar.header("Parâmetros de Análise")
nome_cidade_input = st.sidebar.text_input("Nome da Cidade:", placeholder="Ex: São Paulo")

uploaded_files_input = st.sidebar.file_uploader(
    "Carregue os arquivos CSV:",
    type=["csv"],
    accept_multiple_files=True,
    help="Selecione um ou mais arquivos CSV. Cada arquivo deve conter uma coluna 'Data' e uma coluna 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'."
)

anos_analise_input = st.sidebar.number_input("Número de anos recentes para analisar:", min_value=1, max_value=30, value=5)
limiar_chuva_mm_input = st.sidebar.number_input("Limiar de chuva extrema (mm):", min_value=0.1, value=50.0, step=0.1, format="%.1f")

col1, col2 = st.columns([1,3])

with col1:
    if st.sidebar.button("🔍 Analisar Dados", use_container_width=True, type="primary"):
        if not nome_cidade_input:
            st.sidebar.error("Por favor, insira o nome da cidade.")
        elif not uploaded_files_input:
            st.sidebar.error("Por favor, carregue pelo menos um arquivo CSV.")
        else:
            with st.spinner(f"Analisando dados para {nome_cidade_input}... Por favor, aguarde."):
                # Armazenar os resultados na session_state para persistir entre reruns se necessário
                st.session_state.resultados_analise = analisar_frequencia_chuva_streamlit(
                    uploaded_files_input, 
                    nome_cidade_input, 
                    anos_analise_input, 
                    limiar_chuva_mm_input
                )
    elif 'resultados_analise' not in st.session_state : # Mensagem inicial
         st.info("⬅️ Preencha os parâmetros ao lado e clique em 'Analisar Dados' para começar.")


with col2:
    if 'resultados_analise' in st.session_state:
        resultados = st.session_state.resultados_analise
        
        st.subheader(f"Resultados para: {nome_cidade_input}")
        if resultados["periodo_analisado_str"]:
             st.caption(resultados["periodo_analisado_str"])

        if resultados["contagem_eventos_df"] is not None and not resultados["contagem_eventos_df"].empty:
            st.markdown("#### Frequência Anual de Eventos Extremos")
            
            # Tabela
            st.dataframe(resultados["contagem_eventos_df"].style.format({"Numero de Eventos Extremos": "{:.0f}"}), use_container_width=True)
            
            # Gráfico
            df_grafico = resultados["contagem_eventos_df"].set_index('ano')
            st.bar_chart(df_grafico["Numero de Eventos Extremos"])
            
            # Métrica de Tendência
            if resultados["mensagem_tendencia"]:
                st.markdown("#### Análise de Tendência")
                st.info(resultados["mensagem_tendencia"])
        elif resultados["mensagem_tendencia"]: # Caso não haja eventos, mas haja uma mensagem
             st.info(resultados["mensagem_tendencia"])
        else:
            st.warning("Não foram encontrados dados de eventos extremos para exibir.")


        with st.expander("Ver Logs de Processamento"):
            for msg in resultados["mensagens_status"]:
                if "AVISO:" in msg:
                    st.warning(msg)
                elif "Erro:" in msg or "Falha:" in msg:
                    st.error(msg)
                else:
                    st.write(msg)
    
st.sidebar.markdown("---")
st.sidebar.markdown("Desenvolvido como assistente virtual.")
