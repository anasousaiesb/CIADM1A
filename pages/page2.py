import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import get_cmap

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Análise de Radiação Global (2020-2025)")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV.")

    # Sidebar para seleção de parâmetros
    st.sidebar.header("Filtros de Análise")
    
    # Seleção de ano
    anos_disponiveis = sorted(df_unificado['Ano'].unique())
    ano_selecionado = st.sidebar.selectbox(
        "Selecione o ano:",
        anos_disponiveis,
        index=0  # 2020 por padrão
    )
    
    # Seleção de mês (com opção para todos os meses)
    meses_disponiveis = ['Todos'] + list(range(1, 13))
    mes_selecionado = st.sidebar.selectbox(
        "Selecione o mês:",
        meses_disponiveis,
        index=0  # 'Todos' por padrão
    )
    
    # Seleção de tipo de visualização
    tipo_visualizacao = st.sidebar.radio(
        "Tipo de visualização:",
        ('Comparativo Regional', 'Evolução Temporal', 'Análise Detalhada')
    )

    # Filtrar dados conforme seleção
    df_filtrado = df_unificado[df_unificado['Ano'] == ano_selecionado]
    
    if mes_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Mês'] == mes_selecionado]

    if df_filtrado.empty:
        st.warning(f"Não foram encontrados dados para o ano {ano_selecionado} e mês {mes_selecionado}.")
    else:
        # --- VISUALIZAÇÃO 1: COMPARATIVO REGIONAL ---
        if tipo_visualizacao == 'Comparativo Regional':
            st.subheader(f"Comparativo de Radiação Global por Região - {ano_selecionado}")
            
            if mes_selecionado == 'Todos':
                # Calcular média anual por região
                df_media = df_filtrado.groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)
                titulo_grafico = f'Média Anual de Radiação Global por Região - {ano_selecionado}'
            else:
                # Mostrar dados do mês específico
                df_media = df_filtrado.groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)
                titulo_grafico = f'Média de Radiação Global por Região - Mês {mes_selecionado}/{ano_selecionado}'
            
            # Encontrar a região com maior radiação
            regiao_maior = df_media.idxmax()
            valor_maior = df_media.max()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            cores = ['skyblue'] * len(df_media)
            if regiao_maior in df_media.index:
                indice_regiao = df_media.index.get_loc(regiao_maior)
                cores[indice_regiao] = 'coral'
            
            bars = ax.bar(df_media.index, df_media.values, color=cores)
            
            ax.set_xlabel('Região')
            ax.set_ylabel('Radiação Global (Kj/m²)')
            ax.set_title(titulo_grafico)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Adicionar valores nas barras
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05*valor_maior, 
                        f'{yval:.2f}', ha='center', va='bottom')
            
            st.pyplot(fig)
            
            # Análise textual dinâmica
            st.markdown(f"""
            **Análise:**
            - A região com maior radiação global em {'todos os meses' if mes_selecionado == 'Todos' else f'mês {mes_selecionado}'} de {ano_selecionado} foi **{regiao_maior}**, com média de **{valor_maior:.2f} Kj/m²**.
            - A variação entre regiões foi de **{(df_media.max() - df_media.min()):.2f} Kj/m²**, indicando {'grandes' if (df_media.max() - df_media.min()) > 500 else 'moderadas'} diferenças regionais.
            """)
        
        # --- VISUALIZAÇÃO 2: EVOLUÇÃO TEMPORAL ---
        elif tipo_visualizacao == 'Evolução Temporal':
            st.subheader(f"Evolução Temporal da Radiação Global - {ano_selecionado}")
            
            # Agrupar por mês e região
            df_evolucao = df_filtrado.groupby(['Mês', 'Regiao'])['RADIACAO GLOBAL (Kj/m²)'].mean().unstack()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Cores distintas para cada região
            cmap = get_cmap('tab10')
            for i, regiao in enumerate(df_evolucao.columns):
                ax.plot(df_evolucao.index, df_evolucao[regiao], 
                        marker='o', linestyle='-', 
                        color=cmap(i), 
                        label=regiao)
            
            ax.set_xlabel('Mês')
            ax.set_ylabel('Radiação Global (Kj/m²)')
            ax.set_title(f'Evolução Mensal da Radiação Global por Região - {ano_selecionado}')
            ax.set_xticks(range(1, 13))
            ax.grid(True)
            ax.legend(title='Região')
            
            st.pyplot(fig)
            
            # Análise textual dinâmica
            st.markdown("""
            **Análise:**
            - Este gráfico mostra como a radiação global varia ao longo dos meses para cada região.
            - Padrões sazonais podem ser identificados comparando as curvas de cada região.
            - Meses com picos ou vales podem indicar características climáticas específicas.
            """)
        
        # --- VISUALIZAÇÃO 3: ANÁLISE DETALHADA ---
        elif tipo_visualizacao == 'Análise Detalhada':
            st.subheader(f"Análise Detalhada - {ano_selecionado}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top 5 Meses com Maior Radiação**")
                df_top_meses = df_filtrado.groupby(['Regiao', 'Mês'])['RADIACAO GLOBAL (Kj/m²)'].mean().nlargest(5).reset_index()
                st.dataframe(df_top_meses.style.format({'RADIACAO GLOBAL (Kj/m²)': '{:.2f}'}))
            
            with col2:
                st.markdown("**Top 5 Meses com Menor Radiação**")
                df_bottom_meses = df_filtrado.groupby(['Regiao', 'Mês'])['RADIACAO GLOBAL (Kj/m²)'].mean().nsmallest(5).reset_index()
                st.dataframe(df_bottom_meses.style.format({'RADIACAO GLOBAL (Kj/m²)': '{:.2f}'}))
            
            # Heatmap de radiação por região e mês
            st.markdown("**Mapa de Calor: Radiação por Região e Mês**")
            df_heatmap = df_filtrado.groupby(['Regiao', 'Mês'])['RADIACAO GLOBAL (Kj/m²)'].mean().unstack()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            im = ax.imshow(df_heatmap, cmap='YlOrRd', aspect='auto')
            
            ax.set_xticks(np.arange(len(df_heatmap.columns)))
            ax.set_yticks(np.arange(len(df_heatmap.index)))
            ax.set_xticklabels(df_heatmap.columns)
            ax.set_yticklabels(df_heatmap.index)
            plt.colorbar(im, label='Radiação Global (Kj/m²)')
            ax.set_title(f'Radiação Global por Região e Mês - {ano_selecionado}')
            
            st.pyplot(fig)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
