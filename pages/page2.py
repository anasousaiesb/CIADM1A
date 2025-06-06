import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Análise de Radiação Global Personalizada")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV.")

    # --- FILTROS INTERATIVOS ---
    st.sidebar.header("Filtros de Visualização")
    
    # Selecione as Regiões (checkboxes)
    st.sidebar.subheader("Selecione as Regiões:")
    regioes_disponiveis = sorted(df_unificado['Regiao'].unique())
    regioes_selecionadas = []
    for regiao in regioes_disponiveis:
        if st.sidebar.checkbox(regiao, key=f"reg_{regiao}", value=True):
            regioes_selecionadas.append(regiao)
    
    # Selecione os Anos (checkboxes)
    st.sidebar.subheader("Selecione os Anos:")
    anos_disponiveis = sorted(df_unificado['Ano'].unique())
    anos_selecionados = []
    for ano in anos_disponiveis:
        if st.sidebar.checkbox(str(ano), key=f"ano_{ano}", value=True):
            anos_selecionados.append(ano)
    
    # Selecione a Variável (selectbox)
    st.sidebar.subheader("Selecione a Variável:")
    variavel_selecionada = st.sidebar.selectbox(
        "",
        options=['RADIACAO GLOBAL (Kj/m²)'],  # Pode adicionar mais variáveis se existirem
        index=0
    )

    # Verificar se pelo menos uma região e um ano foram selecionados
    if not regioes_selecionadas or not anos_selecionados:
        st.warning("Selecione pelo menos uma região e um ano para visualizar os dados.")
    else:
        # --- PROCESSAMENTO DOS DADOS FILTRADOS ---
        df_filtrado = df_unificado[
            (df_unificado['Regiao'].isin(regioes_selecionadas)) &
            (df_unificado['Ano'].isin(anos_selecionados))
        ]

        # --- VISUALIZAÇÃO DOS DADOS ---
        st.subheader(f"Dados para as Regiões: {', '.join(regioes_selecionadas)}")
        st.subheader(f"Anos: {', '.join(map(str, anos_selecionados))}")
        
        # Gráfico de linhas por mês e região
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Agrupar dados por mês e região
        df_agrupado = df_filtrado.groupby(['Mês', 'Regiao'])[variavel_selecionada].mean().unstack()
        
        # Plotar cada região selecionada
        for regiao in regioes_selecionadas:
            if regiao in df_agrupado.columns:
                ax.plot(df_agrupado.index, df_agrupado[regiao], marker='o', label=regiao)
        
        ax.set_xlabel('Mês')
        ax.set_ylabel(variavel_selecionada)
        ax.set_title(f'Evolução Mensal da {variavel_selecionada}')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xticks(range(1, 13))
        plt.tight_layout()
        st.pyplot(fig)

        # Tabela com dados resumidos
        st.subheader("Dados Resumidos")
        df_resumo = df_filtrado.groupby(['Ano', 'Regiao', 'Mês'])[variavel_selecionada].mean().unstack(['Ano', 'Regiao'])
        st.dataframe(df_resumo.style.format("{:.2f}"))

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {str(e)}")
