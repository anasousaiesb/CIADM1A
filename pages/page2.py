import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np # Necessário para algumas manipulações e cores
from matplotlib.cm import get_cmap # Para cores de gráficos

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Análise de Radiação Global por Ano (2020-2025)")

try:
    # Ler o arquivo unificado com codificação 'latin1'
    # Esta codificação é frequentemente necessária para arquivos CSV com caracteres especiais em português
    df_unificado = pd.read_csv(caminho_arquivo_unificado, encoding='latin1')

    # --- DEBUG: Imprimir colunas para verificar nomes exatos que o Pandas leu ---
    st.write("---")
    st.write("Colunas encontradas no CSV (para depuração, antes da renomeação):", df_unificado.columns.tolist())
    st.write("---")
    # --- FIM DEBUG ---

    # --- Mapeamento e Renomeação de Colunas para tratar Encoding ---
    # Assegurar que os nomes das colunas são os esperados, corrigindo problemas de encoding
    colunas_mapeamento = {
        'MÃªs': 'Mês',
        'RADIACAO GLOBAL (Kj/mÂ²)': 'RADIACAO GLOBAL (Kj/m²)',
        'PRECIPITAÃ‡ÃƒO TOTAL, HORÃRIO (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'TEMPERATURA MÃXIMA NA HORA ANT. (AUT) (Â°C)': 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÃNIMA NA HORA ANT. (AUT) (Â°C)': 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'
    }

    # Aplicar a renomeação, verificando se o nome 'garbled' existe antes de tentar renomear
    novas_colunas = {}
    for garbled_name, clean_name in colunas_mapeamento.items():
        if garbled_name in df_unificado.columns:
            novas_colunas[garbled_name] = clean_name
    
    if novas_colunas:
        df_unificado.rename(columns=novas_colunas, inplace=True)
    # --- Fim do Mapeamento e Renomeação ---

    # --- Verificações de Colunas Essenciais (agora com nomes limpos) ---
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)', 'Temp_Media'] # Incluí Temp_Media pois era uma coluna de interesse anterior
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV mesmo após a tentativa de correção de encoding/renomeação.")

    # Normalizar a coluna 'Regiao' (remover espaços e padronizar para maiúsculas)
    df_unificado['Regiao'] = df_unificado['Regiao'].astype(str).str.strip().str.upper()

    # Converter 'Mês' para tipo numérico, se necessário
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado.dropna(subset=['Mês'], inplace=True) # Remove linhas com Mês inválido

    # Definir o intervalo de anos
    anos_para_analisar = sorted(df_unificado['Ano'].unique())
    if not anos_para_analisar:
        st.warning("Não foram encontrados dados de ano no arquivo CSV.")
        st.stop()
    
    # Você pode permitir que o usuário selecione os anos ou analisar todos automaticamente
    st.sidebar.header("Filtros de Análise")
    selected_anos = st.sidebar.multiselect(
        "Selecione os Anos para Análise",
        options=anos_para_analisar,
        default=anos_para_analisar # Seleciona todos por padrão
    )

    if not selected_anos:
        st.warning("Por favor, selecione pelo menos um ano para análise.")
        st.stop()

    # Iterar sobre os anos selecionados
    for ano_selecionado in sorted(selected_anos):
        st.markdown(f"## Análise para o Ano: {ano_selecionado}")

        df_ano_atual = df_unificado[df_unificado['Ano'] == ano_selecionado].copy()

        if df_ano_atual.empty:
            st.warning(f"Não foram encontrados dados para o ano de {ano_selecionado}.")
            continue # Pula para o próximo ano na iteração
        else:
            # Encontrar a maior média de radiação para o ano atual
            df_media_mensal_radiacao_ano = df_ano_atual[['Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']]
            
            # Agrupar por Regiao e Mês para encontrar a média se houver múltiplas entradas (ex: de diferentes estados dentro da mesma região)
            # e então encontrar o máximo de radiação global para a combinação Regiao/Mês
            grouped_data = df_media_mensal_radiacao_ano.groupby(['Regiao', 'Mês'])['RADIACAO GLOBAL (Kj/m²)'].mean().reset_index()

            if grouped_data.empty:
                st.warning(f"Não há dados agregados para radiação global no ano {ano_selecionado}.")
                continue

            idx_maior_radiacao_geral_ano = grouped_data['RADIACAO GLOBAL (Kj/m²)'].idxmax()
            maior_media_geral_ano = grouped_data.loc[idx_maior_radiacao_geral_ano]

            regiao_maior_media_ano = maior_media_geral_ano['Regiao']
            mes_maior_media_ano = int(maior_media_geral_ano['Mês']) # Convertendo para int
            valor_maior_media_ano = maior_media_geral_ano['RADIACAO GLOBAL (Kj/m²)']

            st.subheader("Resultado da Análise para este ano:")
            st.write(
                f"A região que apresentou a maior média de radiação global em um único mês durante **{ano_selecionado}** foi a **{regiao_maior_media_ano}**."
            )
            st.write(
                f"Isso ocorreu no **Mês {mes_maior_media_ano}**."
            )
            st.write(
                f"A média aproximada de radiação global foi de **{valor_maior_media_ano:.2f} Kj/m²**."
            )

            # --- CÓDIGO PARA GERAR O GRÁFICO DO RESULTADO ESPECÍFICO PARA O ANO ATUAL ---
            st.subheader(f"Comparativo da Radiação Global em {mes_maior_media_ano}/{ano_selecionado} por Região")

            # Filtrar dados para o mês e ano de maior radiação (do ano atual)
            df_mes_especifico_ano = df_ano_atual[df_ano_atual['Mês'] == mes_maior_media_ano]

            # Calcular a média de radiação por região para este mês específico do ano atual
            media_radiacao_mes_especifico_por_regiao_ano = df_mes_especifico_ano.groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)

            if media_radiacao_mes_especifico_por_regiao_ano.empty:
                st.warning(f"Não foram encontrados dados de radiação para todas as regiões no mês {mes_maior_media_ano} de {ano_selecionado}.")
            else:
                fig_resultado_ano, ax_resultado_ano = plt.subplots(figsize=(10, 6))
                
                cores = ['skyblue'] * len(media_radiacao_mes_especifico_por_regiao_ano)
                # Destacar a região com a maior média
                if regiao_maior_media_ano in media_radiacao_mes_especifico_por_regiao_ano.index:
                    indice_regiao_destaque = media_radiacao_mes_especifico_por_regiao_ano.index.get_loc(regiao_maior_media_ano)
                    cores[indice_regiao_destaque] = 'coral'
                
                bars = ax_resultado_ano.bar(media_radiacao_mes_especifico_por_regiao_ano.index, media_radiacao_mes_especifico_por_regiao_ano.values, color=cores)
                
                ax_resultado_ano.set_xlabel('Região')
                ax_resultado_ano.set_ylabel('Radiação Global Média (Kj/m²)')
                ax_resultado_ano.set_title(f'Média de Radiação Global por Região - Mês {mes_maior_media_ano}/{ano_selecionado}')
                ax_resultado_ano.set_xticks(media_radiacao_mes_especifico_por_regiao_ano.index)
                ax_resultado_ano.grid(axis='y', linestyle='--', alpha=0.7)

                # Adicionar valores no topo das barras
                for bar in bars:
                    yval = bar.get_height()
                    # Garante que o texto não fique muito alto em barras pequenas
                    text_y_offset = 0.05 * valor_maior_media_ano if valor_maior_media_ano > 0 else 1 
                    plt.text(bar.get_x() + bar.get_width()/2.0, yval + text_y_offset, f'{yval:.2f}', ha='center', va='bottom')

                plt.tight_layout()
                st.pyplot(fig_resultado_ano)
            
        st.markdown("---") # Separador visual entre os anos

    # --- Seção para um comparativo geral (opcional) ---
    st.subheader("Análise Comparativa de Radiação Global ao longo dos anos")
    st.write("Aqui você pode adicionar gráficos que comparam a radiação global entre diferentes anos ou regiões ao longo do tempo.")

    # Exemplo: Gráfico de linha da radiação média anual por região
    st.subheader("Radiação Global Média Anual por Região")
    df_radiacao_anual_regiao = df_unificado.groupby(['Ano', 'Regiao'])['RADIACAO GLOBAL (Kj/m²)'].mean().unstack()

    if not df_radiacao_anual_regiao.empty:
        fig_anual_comp, ax_anual_comp = plt.subplots(figsize=(12, 7))
        # Gerar cores para cada região
        regioes_unicas = df_radiacao_anual_regiao.columns
        cmap_regiao = get_cmap('tab10') # Um mapa de cores bom para categorias
        cores_regioes = {reg: cmap_regiao(i) for i, reg in enumerate(regioes_unicas)}

        for regiao in regioes_unicas:
            ax_anual_comp.plot(df_radiacao_anual_regiao.index, df_radiacao_anual_regiao[regiao], 
                               marker='o', linestyle='-', label=regiao, color=cores_regioes[regiao])
        
        ax_anual_comp.set_title('Radiação Global Média Anual por Região (2020-2025)')
        ax_anual_comp.set_xlabel('Ano')
        ax_anual_comp.set_ylabel('Radiação Global Média (Kj/m²)')
        ax_anual_comp.set_xticks(anos_para_analisar)
        ax_anual_comp.grid(True)
        ax_anual_comp.legend(title='Região', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig_anual_comp)
    else:
        st.info("Não há dados suficientes para gerar o gráfico de radiação global média anual por região.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo (após o tratamento de encoding).")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
    st.exception(e) # Imprime o traceback completo para depuração
