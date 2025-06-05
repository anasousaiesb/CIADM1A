import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Análise de Temperatura Máxima Média - Brasil 2021")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Exibir as colunas disponíveis para ajudar na verificação
    st.write("Colunas disponíveis no arquivo CSV:", df_unificado.columns.tolist())

    # Nome correto da coluna de temperatura máxima
    coluna_temp_max = "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)"

    # Certificar que a coluna de temperatura existe
    if coluna_temp_max not in df_unificado.columns:
        st.error(f"Erro: A coluna '{coluna_temp_max}' não foi encontrada no arquivo CSV.")
    else:
        # Filtrar apenas o ano de 2021
        df_2021 = df_unificado[df_unificado['Ano'] == 2021]

        # Lista de regiões únicas
        regioes = df_2021['Regiao'].unique()

        # Agrupar por região e mês, calculando a média da temperatura máxima
        df_agrupado = df_2021.groupby(['Regiao', 'Mês'])[coluna_temp_max].mean().reset_index()

        # Verificar se há dados após o agrupamento
        if df_agrupado.empty:
            st.error("Erro: Não há dados disponíveis para análise após o agrupamento.")
        else:
            # Encontrar a região com temperatura máxima média mais alta durante o ano
            regiao_mais_quente = df_agrupado.groupby('Regiao')[coluna_temp_max].mean().idxmax()

            # Filtrar apenas os meses de inverno
            meses_inverno = ['Junho', 'Julho', 'Agosto']
            df_inverno = df_agrupado[df_agrupado['Mês'].isin(meses_inverno)]

            # Verificar se há dados para os meses de inverno
            if df_inverno.empty:
                st.error("Erro: Não há dados disponíveis para os meses de inverno.")
            else:
                # Encontrar a região com temperatura máxima média mais baixa nos meses de inverno
                regiao_mais_fria = df_inverno.groupby('Regiao')[coluna_temp_max].mean().idxmin()

                # Exibir resultados
                st.subheader(f"Região mais quente de 2021: {regiao_mais_quente}")
                st.subheader(f"Região mais fria nos meses de inverno de 2021: {regiao_mais_fria}")

                # Visualização gráfica das temperaturas máximas
                fig, ax = plt.subplots(figsize=(8, 5))
                for regiao in regioes:
                    df_regiao = df_agrupado[df_agrupado['Regiao'] == regiao]
                    ax.plot(df_regiao['Mês'], df_regiao[coluna_temp_max], marker='o', label=regiao)

                ax.set_title('Temperatura Máxima Média por Região - 2021')
                ax.set_xlabel('Mês')
                ax.set_ylabel('Temperatura Máxima Média (°C)')
                ax.set_xticklabels(df_agrupado['Mês'].unique(), rotation=45)
                ax.legend(title='Região')
                ax.grid(True)
                plt.tight_layout()
                st.pyplot(fig)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao processar os dados: {e}")
