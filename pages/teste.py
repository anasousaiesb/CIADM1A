import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np # Necessário para algumas manipulações e cores

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Análise de Radiação Global em 2020")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV.")

    # Filtrar dados para o ano de 2020
    df_2020 = df_unificado[df_unificado['Ano'] == 2020].copy()

    if df_2020.empty:
        st.warning("Não foram encontrados dados para o ano de 2020.")
    else:
        # --- INÍCIO DA LÓGICA PARA ENCONTRAR O RESULTADO PRINCIPAL ---
        # (Como no script anterior, para encontrar a região e o mês com a maior média)
        df_media_mensal_radiacao_2020 = df_2020[['Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']]
        idx_maior_radiacao_geral = df_media_mensal_radiacao_2020['RADIACAO GLOBAL (Kj/m²)'].idxmax()
        maior_media_geral = df_media_mensal_radiacao_2020.loc[idx_maior_radiacao_geral]

        regiao_maior_media = maior_media_geral['Regiao']
        mes_maior_media = int(maior_media_geral['Mês']) # Convertendo para int para uso posterior
        valor_maior_media = maior_media_geral['RADIACAO GLOBAL (Kj/m²)']

        st.subheader("Resultado da Análise para 2020:")
        st.write(
            f"A região que apresentou a maior média de radiação global em um único mês durante o ano de 2020 foi a **{regiao_maior_media}**."
        )
        st.write(
            f"Isso ocorreu no **Mês {mes_maior_media}**."
        )
        st.write(
            f"A média aproximada de radiação global foi de **{valor_maior_media:.2f} Kj/m²**."
        )
        # --- FIM DA LÓGICA PARA ENCONTRAR O RESULTADO PRINCIPAL ---

        # --- INÍCIO DO CÓDIGO PARA GERAR O GRÁFICO DO RESULTADO ESPECÍFICO ---
        st.subheader(f"Comparativo da Radiação Global em {mes_maior_media}/2020 por Região")

        # Filtrar dados para o mês e ano de maior radiação (Outubro de 2020)
        df_mes_especifico = df_2020[df_2020['Mês'] == mes_maior_media]

        # Calcular a média de radiação por região para este mês específico
        # Se já houver uma única entrada por Regiao/Mês, o groupby não mudará o valor, mas garante a estrutura.
        # Se houver múltiplas estações por região, isso calculará a média regional para o mês.
        media_radiacao_mes_especifico_por_regiao = df_mes_especifico.groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)

        if media_radiacao_mes_especifico_por_regiao.empty:
            st.warning(f"Não foram encontrados dados de radiação para todas as regiões no mês {mes_maior_media} de 2020.")
        else:
            fig_resultado, ax_resultado = plt.subplots(figsize=(10, 6))
            
            cores = ['skyblue'] * len(media_radiacao_mes_especifico_por_regiao)
            # Destacar a região com a maior média
            if regiao_maior_media in media_radiacao_mes_especifico_por_regiao.index:
                indice_regiao_destaque = media_radiacao_mes_especifico_por_regiao.index.get_loc(regiao_maior_media)
                cores[indice_regiao_destaque] = 'coral'
            
            bars = ax_resultado.bar(media_radiacao_mes_especifico_por_regiao.index, media_radiacao_mes_especifico_por_regiao.values, color=cores)
            
            ax_resultado.set_xlabel('Região')
            ax_resultado.set_ylabel('Radiação Global Média (Kj/m²)')
            ax_resultado.set_title(f'Média de Radiação Global por Região - Mês {mes_maior_media}/2020')
            ax_resultado.set_xticks(media_radiacao_mes_especifico_por_regiao.index)
            ax_resultado.grid(axis='y', linestyle='--', alpha=0.7)

            # Adicionar valores no topo das barras
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * valor_maior_media, f'{yval:.2f}', ha='center', va='bottom')

            plt.tight_layout()
            st.pyplot(fig_resultado)
        # --- FIM DO CÓDIGO PARA GERAR O GRÁFICO DO RESULTADO ESPECÍFICO ---

        st.markdown("---") # Separador visual
        # ... (o restante do seu código de visualização interativa pode continuar aqui) ...
        # st.title("Médias Mensais Regionais (2020-2025) - Facetado por Região e Variável")
        # (coloque o código dos gráficos facetados aqui, se desejar mantê-los)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
