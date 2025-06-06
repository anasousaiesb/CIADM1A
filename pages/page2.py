import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Análise Dinâmica de Radiação Global (2020-2025)")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV.")

    # Widgets de seleção na sidebar
    st.sidebar.header("Filtros")
    ano_selecionado = st.sidebar.selectbox(
        "Selecione o ano:",
        options=sorted(df_unificado['Ano'].unique()),
        index=0  # 2020 como padrão
    )
    
    meses_disponiveis = sorted(df_unificado[df_unificado['Ano'] == ano_selecionado]['Mês'].unique())
    mes_selecionado = st.sidebar.selectbox(
        "Selecione o mês:",
        options=meses_disponiveis,
        index=0  # Primeiro mês como padrão
    )

    # Filtrar dados para o ano selecionado
    df_ano = df_unificado[df_unificado['Ano'] == ano_selecionado].copy()

    if df_ano.empty:
        st.warning(f"Não foram encontrados dados para o ano de {ano_selecionado}.")
    else:
        # --- ENCONTRAR A MAIOR MÉDIA NO ANO SELECIONADO ---
        df_media_mensal_radiacao = df_ano[['Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']]
        idx_maior_radiacao_geral = df_media_mensal_radiacao['RADIACAO GLOBAL (Kj/m²)'].idxmax()
        maior_media_geral = df_media_mensal_radiacao.loc[idx_maior_radiacao_geral]

        regiao_maior_media = maior_media_geral['Regiao']
        mes_maior_media = int(maior_media_geral['Mês'])
        valor_maior_media = maior_media_geral['RADIACAO GLOBAL (Kj/m²)']

        st.subheader(f"Resultado da Análise para {ano_selecionado}:")
        st.write(
            f"A região que apresentou a maior média de radiação global em um único mês durante o ano de {ano_selecionado} foi a **{regiao_maior_media}**."
        )
        st.write(
            f"Isso ocorreu no **Mês {mes_maior_media}**."
        )
        st.write(
            f"A média aproximada de radiação global foi de **{valor_maior_media:.2f} Kj/m²**."
        )

        # --- GRÁFICO PARA O MÊS SELECIONADO ---
        st.subheader(f"Comparativo da Radiação Global em {mes_selecionado}/{ano_selecionado} por Região")

        # Filtrar dados para o mês e ano selecionados
        df_mes_selecionado = df_ano[df_ano['Mês'] == mes_selecionado]

        # Calcular a média de radiação por região para este mês
        media_radiacao_mes_selecionado = df_mes_selecionado.groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)

        if media_radiacao_mes_selecionado.empty:
            st.warning(f"Não foram encontrados dados de radiação para todas as regiões no mês {mes_selecionado} de {ano_selecionado}.")
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Cores dinâmicas - destacar a região com maior média se for o mesmo mês
            cores = ['skyblue'] * len(media_radiacao_mes_selecionado)
            if mes_selecionado == mes_maior_media:
                if regiao_maior_media in media_radiacao_mes_selecionado.index:
                    indice_regiao_destaque = media_radiacao_mes_selecionado.index.get_loc(regiao_maior_media)
                    cores[indice_regiao_destaque] = 'coral'
            
            bars = ax.bar(media_radiacao_mes_selecionado.index, media_radiacao_mes_selecionado.values, color=cores)
            
            ax.set_xlabel('Região')
            ax.set_ylabel('Radiação Global Média (Kj/m²)')
            ax.set_title(f'Média de Radiação Global por Região - Mês {mes_selecionado}/{ano_selecionado}')
            ax.set_xticks(media_radiacao_mes_selecionado.index)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Adicionar valores no topo das barras
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * yval, f'{yval:.2f}', ha='center', va='bottom')

            plt.tight_layout()
            st.pyplot(fig)

        # --- GRÁFICO DE LINHAS PARA COMPARAÇÃO ANUAL ---
        st.subheader(f"Evolução Mensal da Radiação Global em {ano_selecionado}")

        # Calcular média mensal por região
        df_media_mensal_regiao = df_ano.groupby(['Regiao', 'Mês'])['RADIACAO GLOBAL (Kj/m²)'].mean().unstack('Regiao')

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        for regiao in df_media_mensal_regiao.columns:
            ax2.plot(df_media_mensal_regiao.index, df_media_mensal_regiao[regiao], marker='o', label=regiao)
        
        # Destacar o mês selecionado
        ax2.axvline(x=mes_selecionado, color='gray', linestyle='--', alpha=0.5)
        ax2.text(mes_selecionado, ax2.get_ylim()[1]*0.95, f'Mês selecionado: {mes_selecionado}', 
                ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8))

        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Radiação Global Média (Kj/m²)')
        ax2.set_title(f'Evolução Mensal da Radiação Global por Região - {ano_selecionado}')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig2)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
