import pandas as pd
import streamlit as st # Removido matplotlib.pyplot, pois não será usado para esta resposta específica
import os

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
    df_2020 = df_unificado[df_unificado['Ano'] == 2020].copy() # Usar .copy() para evitar SettingWithCopyWarning

    if df_2020.empty:
        st.warning("Não foram encontrados dados para o ano de 2020.")
    else:
        # Calcular a média mensal de radiação global por região para 2020
        # Assegurar que 'Mês' e 'Regiao' são tratados como categóricos ou strings para agrupamento, se necessário
        # (Pandas geralmente lida bem com isso, mas é um ponto a observar)
        
        # A média já deve estar calculada como 'RADIACAO GLOBAL (Kj/m²)' se o arquivo CSV
        # representa médias mensais. Se 'RADIACAO GLOBAL (Kj/m²)' no CSV for diária ou horária,
        # seria necessário agrupar por Mês e Regiao e calcular a média.
        # Assumindo que 'RADIACAO GLOBAL (Kj/m²)' já é a média mensal por estação/ponto de coleta.
        # Se for preciso calcular a média mensal a partir de dados mais granulares:
        # df_media_mensal_radiacao_2020 = df_2020.groupby(['Regiao', 'Mês'])['RADIACAO GLOBAL (Kj/m²)'].mean().reset_index()
        
        # Se 'RADIACAO GLOBAL (Kj/m²)' já for a média mensal para cada combinação de Regiao/Mês no arquivo:
        df_media_mensal_radiacao_2020 = df_2020[['Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']]

        # Encontrar a maior média de radiação
        # idx_maior_radiacao = df_media_mensal_radiacao_2020['RADIACAO GLOBAL (Kj/m²)'].idxmax()
        # resultado = df_media_mensal_radiacao_2020.loc[idx_maior_radiacao]
        
        # Para garantir que estamos pegando a maior média *mensal* por *região*
        # Primeiro, vamos encontrar a maior média para cada região e mês
        # Se o seu CSV já tiver uma linha por Região/Mês com a média, o passo acima é suficiente.
        # Se houver múltiplas entradas por Região/Mês (ex: várias estações por região),
        # e 'RADIACAO GLOBAL (Kj/m²)' é a média dessas estações para aquele mês:
        
        # Encontra o índice da linha com o maior valor na coluna 'RADIACAO GLOBAL (Kj/m²)'
        # dentro dos dados de 2020.
        idx_maior_radiacao_geral = df_media_mensal_radiacao_2020['RADIACAO GLOBAL (Kj/m²)'].idxmax()
        
        # Obtém a linha inteira correspondente a essa maior média
        maior_media_geral = df_media_mensal_radiacao_2020.loc[idx_maior_radiacao_geral]

        regiao_maior_media = maior_media_geral['Regiao']
        mes_maior_media = maior_media_geral['Mês']
        valor_maior_media = maior_media_geral['RADIACAO GLOBAL (Kj/m²)']

        st.subheader("Resultado da Análise para 2020:")
        st.write(
            f"A região que apresentou a maior média de radiação global em um único mês durante o ano de 2020 foi a **{regiao_maior_media}**."
        )
        st.write(
            f"Isso ocorreu no **Mês {int(mes_maior_media)}** (lembre-se que, de acordo com sua solicitação, estou tentando pronunciar corretamente e, caso minha pronúncia da palavra 'mês' esteja incorreta, peço que me corrija)."
        )
        st.write(
            f"A média aproximada de radiação global foi de **{valor_maior_media:.2f} Kj/m²**."
        )
        
        # --- Trecho do seu código original para visualização (pode ser mantido se desejado) ---
        # O código abaixo é para a visualização interativa e pode ser executado em seguida
        # ou removido se o objetivo for apenas a pergunta específica.
        
        st.markdown("---") # Separador visual
        st.title("Médias Mensais Regionais (2020-2025) - Facetado por Região e Variável")

        # Calcular a média da temperatura (se necessário para outras partes do app)
        if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns and \
           'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns:
            df_unificado['Temperatura Média (°C)'] = (
                df_unificado['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
                df_unificado['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
            ) / 2
        else:
            st.warning("Colunas de temperatura máxima ou mínima não encontradas. O cálculo da 'Temperatura Média (°C)' foi ignorado.")
            # Adicionar a coluna com NaN ou um valor padrão se outras partes do código esperam que ela exista
            df_unificado['Temperatura Média (°C)'] = pd.NA


        # Lista de regiões e anos únicas
        regioes = sorted(df_unificado['Regiao'].unique())
        anos = sorted(df_unificado['Ano'].unique())
        # Meses precisam ser numéricos e ordenados para o gráfico.
        # Se 'Mês' não for numérico ou estiver desordenado, ajuste aqui.
        meses_disponiveis = sorted(df_unificado['Mês'].unique())


        # Variáveis a serem plotadas
        variaveis = {
            'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
        }
        # Adicionar outras variáveis se existirem e forem necessárias
        if 'Temperatura Média (°C)' in df_unificado.columns:
            variaveis['Temperatura Média (°C)'] = 'Temperatura Média (°C)'
        if 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' in df_unificado.columns:
            variaveis['Precipitação Total (mm)'] = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'


        # Seleção interativa da variável
        if variaveis: # Apenas mostra o selectbox se houver variáveis para selecionar
            nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()))
            coluna_var = variaveis[nome_var]

            # Cores para os anos (importar bibliotecas se ainda não importadas)
            import numpy as np
            from matplotlib.cm import get_cmap
            import matplotlib.pyplot as plt # Importar aqui para o plot

            cmap = get_cmap('viridis')
            cores_anos = {ano: cmap(i/len(anos)) for i, ano in enumerate(anos)}

            # Gráfico facetado por região
            st.subheader(f"Média Mensal de {nome_var} por Região ({min(anos)}-{max(anos)})")
            
            # Determinar o número de colunas para os subplots, máximo de 3 por linha
            n_cols_plot = min(len(regioes), 3)
            n_rows_plot = (len(regioes) - 1) // n_cols_plot + 1
            
            fig, axes = plt.subplots(nrows=n_rows_plot, ncols=n_cols_plot, figsize=(5*n_cols_plot, 5*n_rows_plot), sharey=True, squeeze=False)
            axes = axes.flatten() # Para fácil iteração

            for i, regiao in enumerate(regioes):
                ax = axes[i]
                df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
                for ano in anos:
                    # Certifique-se de que 'Mês' é numérico para o groupby e reindex
                    df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses_disponiveis)
                    if not df_ano_regiao.empty:
                        ax.plot(meses_disponiveis, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
                ax.set_title(regiao)
                ax.set_xlabel('Mês')
                if i % n_cols_plot == 0: # Apenas o primeiro eixo Y de cada linha
                    ax.set_ylabel(nome_var)
                ax.set_xticks(meses_disponiveis) # Definir os ticks para os meses disponíveis
                ax.set_xticklabels([int(m) for m in meses_disponiveis]) # Mostrar como inteiros se forem numéricos
                ax.grid(True)
            
            # Remover eixos não utilizados se houver
            for j in range(i + 1, len(axes)):
                fig.delaxes(axes[j])

            # Adicionar legenda fora dos subplots
            # Apenas pega handles e labels do último eixo que foi plotado e teve dados
            handles, labels = [], []
            for ax_leg in axes: # Iterar para encontrar um eixo com legenda
                h_temp, l_temp = ax_leg.get_legend_handles_labels()
                if h_temp: # Se encontrou handles
                    # Manter apenas labels únicos para a legenda
                    unique_labels = {}
                    for handle, label in zip(h_temp, l_temp):
                        if label not in unique_labels:
                            unique_labels[label] = handle
                    handles = list(unique_labels.values())
                    labels = list(unique_labels.keys())
                    break # Sai do loop assim que encontrar legendas

            if handles and labels: # Apenas adiciona legenda se houver algo para legendar
                 fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.05, 1))


            plt.tight_layout(rect=[0, 0, 0.92, 1]) # Ajustar rect para a legenda
            st.pyplot(fig)
        else:
            st.warning("Nenhuma variável disponível para plotagem. Verifique as colunas do arquivo CSV.")


except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
