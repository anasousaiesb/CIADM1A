import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
from glob import glob

st.title("Análise Personalizada de Radiação Global (2020-2025)")

# Função para carregar e consolidar os dados
def carregar_dados():
    # Padrão para encontrar os arquivos
    padrao_arquivos = os.path.join("CIADM1A", "medias", "medias_mensais_geo_temp_media_*.csv")
    arquivos = glob(padrao_arquivos)
    
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo encontrado com o padrão: {padrao_arquivos}")
    
    dfs = []
    for arquivo in arquivos:
        try:
            # Extrair o ano do nome do arquivo
            ano = int(arquivo.split('_')[-1].replace('.csv', ''))
            df = pd.read_csv(arquivo)
            df['Ano'] = ano  # Adiciona a coluna de ano
            dfs.append(df)
        except Exception as e:
            st.warning(f"Erro ao processar arquivo {arquivo}: {str(e)}")
            continue
    
    if not dfs:
        raise ValueError("Nenhum dado válido foi carregado dos arquivos.")
    
    df_unificado = pd.concat(dfs, ignore_index=True)
    
    # Verificar e limpar dados
    df_unificado['Ano'] = pd.to_numeric(df_unificado['Ano'], errors='coerce')
    df_unificado = df_unificado.dropna(subset=['Ano'])
    
    return df_unificado

try:
    # Carregar dados consolidados
    df_unificado = carregar_dados()

    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada nos arquivos CSV.")

    # Widgets de seleção na sidebar
    st.sidebar.header("Selecione os Filtros")
    
    # Obter anos únicos, ordenados e sem duplicatas
    anos_disponiveis = sorted(df_unificado['Ano'].unique())
    
    # Mostrar anos disponíveis na sidebar
    st.sidebar.markdown("### Anos disponíveis no dataset:")
    st.sidebar.write(anos_disponiveis)
    
    # Selecionar ano
    ano_selecionado = st.sidebar.selectbox(
        "Ano:",
        options=anos_disponiveis,
        index=len(anos_disponiveis)-1  # Seleciona o último ano por padrão
    )
    
    # Dicionário de meses
    meses_nome = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    # Filtrar meses disponíveis para o ano selecionado
    meses_disponiveis = sorted(df_unificado[df_unificado['Ano'] == ano_selecionado]['Mês'].unique())
    meses_nome_disponiveis = [meses_nome[mes] for mes in meses_disponiveis]
    
    # Selecionar mês
    mes_selecionado_nome = st.sidebar.selectbox(
        "Mês:",
        options=meses_nome_disponiveis,
        index=0  # Sempre começa com o primeiro mês disponível
    )
    
    # Obter o número do mês selecionado
    mes_selecionado = [num for num, nome in meses_nome.items() if nome == mes_selecionado_nome][0]
    
    # Selecionar região
    regioes_disponiveis = sorted(df_unificado['Regiao'].unique())
    regiao_selecionada = st.sidebar.selectbox(
        "Região:",
        options=regioes_disponiveis,
        index=0  # Sempre começa com a primeira região disponível
    )

    # --- ANÁLISE PARA O ANO, MÊS E REGIÃO SELECIONADOS ---
    st.subheader(f"Análise para {mes_selecionado_nome} de {ano_selecionado} - Região {regiao_selecionada}")

    # Filtrar dados para a seleção
    df_filtrado = df_unificado[
        (df_unificado['Ano'] == ano_selecionado) &
        (df_unificado['Mês'] == mes_selecionado) &
        (df_unificado['Regiao'] == regiao_selecionada)
    ]

    if df_filtrado.empty:
        st.warning(f"Não foram encontrados dados para a região {regiao_selecionada} em {mes_selecionado_nome}/{ano_selecionado}.")
    else:
        # Calcular média para a região selecionada
        media_regiao = df_filtrado['RADIACAO GLOBAL (Kj/m²)'].mean()
        
        # Comparar com a média geral do mês
        media_geral_mes = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Mês'] == mes_selecionado)
        ]['RADIACAO GLOBAL (Kj/m²)'].mean()
        
        # Comparar com a média anual da região
        media_anual_regiao = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Regiao'] == regiao_selecionada)
        ]['RADIACAO GLOBAL (Kj/m²)'].mean()

        # Exibir métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Radiação em {mes_selecionado_nome}",
                value=f"{media_regiao:.2f} Kj/m²",
                delta=f"{(media_regiao - media_geral_mes):.2f} vs média geral do mês"
            )
        with col2:
            st.metric(
                label="Média Geral do Mês",
                value=f"{media_geral_mes:.2f} Kj/m²"
            )
        with col3:
            st.metric(
                label="Média Anual da Região",
                value=f"{media_anual_regiao:.2f} Kj/m²",
                delta=f"{(media_regiao - media_anual_regiao):.2f} vs média anual"
            )

        # --- GRÁFICO DE COMPARAÇÃO REGIONAL ---
        st.subheader(f"Comparação Regional para {mes_selecionado_nome}/{ano_selecionado}")

        # Dados para comparação
        df_comparacao = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Mês'] == mes_selecionado)
        ].groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Cores - destacar a região selecionada
        cores = ['lightgray' if regiao != regiao_selecionada else 'coral' 
                for regiao in df_comparacao.index]
        
        bars = ax.bar(df_comparacao.index, df_comparacao.values, color=cores)
        
        ax.set_xlabel('Região')
        ax.set_ylabel('Radiação Global Média (Kj/m²)')
        ax.set_title(f'Comparação Regional - {mes_selecionado_nome}/{ano_selecionado}')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Adicionar valores nas barras
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05*yval, 
                   f'{yval:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        st.pyplot(fig)

        # --- EVOLUÇÃO MENSAL DA REGIÃO SELECIONADA ---
        st.subheader(f"Evolução Mensal em {ano_selecionado} - Região {regiao_selecionada}")

        df_evolucao = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Regiao'] == regiao_selecionada)
        ].groupby('Mês')['RADIACAO GLOBAL (Kj/m²)'].mean()

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(df_evolucao.index, df_evolucao.values, marker='o', color='coral')
        
        # Destacar o mês selecionado
        ax2.axvline(x=mes_selecionado, color='gray', linestyle='--', alpha=0.5)
        ax2.text(mes_selecionado, ax2.get_ylim()[1]*0.9, 
                f'Mês selecionado\n{mes_selecionado_nome}', 
                ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8))

        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Radiação Global Média (Kj/m²)')
        ax2.set_title(f'Evolução Mensal - Região {regiao_selecionada} - {ano_selecionado}')
        ax2.set_xticks(range(1, 13))
        ax2.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig2)

        # --- EXPLICAÇÕES DOS GRÁFICOS ---
        st.subheader("Explicações dos Gráficos")
        
        with st.expander("Gráfico de Comparação Regional"):
            st.write(f"""
            Este gráfico de barras compara a radiação solar média entre todas as regiões disponíveis para o mês de **{mes_selecionado_nome} de {ano_selecionado}**.
            
            - A região **{regiao_selecionada}** está destacada em coral para fácil identificação
            - As barras estão ordenadas da maior para a menor radiação
            - Os valores exatos são mostrados no topo de cada barra
            - Este gráfico permite identificar como a região selecionada se compara com as demais no mesmo período
            """)
        
        with st.expander("Gráfico de Evolução Mensal"):
            st.write(f"""
            Este gráfico de linha mostra a variação da radiação solar ao longo do ano **{ano_selecionado}** para a região **{regiao_selecionada}**.
            
            - Cada ponto representa a média mensal de radiação
            - A linha vermelha tracejada marca o mês selecionado (**{mes_selecionado_nome}**)
            - Permite visualizar padrões sazonais e identificar meses com maior ou menor radiação
            - O valor exato de cada mês pode ser visto passando o mouse sobre os pontos (no modo interativo)
            """)

except FileNotFoundError as e:
    st.error(f"Erro: {str(e)}")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada nos arquivos CSV. Verifique os nomes das colunas.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {str(e)}")
