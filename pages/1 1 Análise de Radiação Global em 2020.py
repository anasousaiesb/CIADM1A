import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Análise Personalizada de Radiação Global (2020-2025)")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV.")

    # Widgets de seleção na sidebar
    st.sidebar.header("Selecione os Filtros")
    
    # Selecionar ano
    anos_disponiveis = sorted(df_unificado['Ano'].unique())
    ano_selecionado = st.sidebar.selectbox(
        "Ano:",
        options=anos_disponiveis,
        index=len(anos_disponiveis)-1 if 2023 not in anos_disponiveis else anos_disponiveis.index(2023)
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

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {str(e)}")
