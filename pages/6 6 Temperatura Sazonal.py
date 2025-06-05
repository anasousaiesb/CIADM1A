import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Análise Comparativa de Temperaturas Médias Mensais (2020-2025)")
st.subheader("Regiões Sudeste e Nordeste")

try:
    # Ler o arquivo unificado com codificação específica
    df_unificado = pd.read_csv(caminho_arquivo_unificado, encoding='latin1')
    
    # Exibir colunas para depuração
    st.write("---")
    st.write("Colunas encontradas no CSV:", df_unificado.columns.tolist())
    st.write("---")

    # Renomeando a coluna para garantir compatibilidade
    df_unificado.rename(columns={'MÃªs': 'Mês'}, inplace=True)

    # Normaliza a coluna 'Regiao'
    if 'Regiao' in df_unificado.columns:
        df_unificado['Regiao'] = df_unificado['Regiao'].astype(str).str.strip().str.upper()
    else:
        st.error("Erro: A coluna 'Regiao' não foi encontrada no arquivo CSV.")
        st.stop()
    
    # Verificação das colunas essenciais
    colunas_essenciais = ['Mês', 'Temp_Media', 'Ano']
    for col in colunas_essenciais:
        if col not in df_unificado.columns:
            st.error(f"Erro: A coluna '{col}' não foi encontrada no arquivo CSV.")
            st.stop()

    # Certifica que 'Mês' é numérico para ordenação
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado.dropna(subset=['Mês'], inplace=True)
    meses = sorted(df_unificado['Mês'].unique()) 
    anos = sorted(df_unificado['Ano'].unique())

    # Variável a ser analisada
    nome_var = 'Temperatura Média (°C)'
    coluna_var = 'Temp_Media'

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Gráfico para a Região Sudeste
    st.markdown("---")
    st.subheader(f"{nome_var} na Região Sudeste (2020-2025)")
    
    df_sudeste = df_unificado[df_unificado['Regiao'] == 'SUDESTE']
    
    if df_sudeste.empty:
        st.warning("Dados para a Região Sudeste não encontrados.")
    else:
        fig_sudeste, ax_sudeste = plt.subplots(figsize=(10, 6))
        df_ano_sudeste_grouped = df_sudeste.groupby(['Ano', 'Mes'])[coluna_var].mean().unstack(level=0)

        for ano in anos:
            if ano in df_ano_sudeste_grouped.columns:
                ax_sudeste.plot(meses, df_ano_sudeste_grouped[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        
        ax_sudeste.set_title(f'Média Mensal de {nome_var} - Sudeste (2020-2025)')
        ax_sudeste.set_xlabel('Mês')
        ax_sudeste.set_ylabel(nome_var)
        ax_sudeste.set_xticks(meses)
        ax_sudeste.grid(True)
        ax_sudeste.legend(title='Ano')
        plt.tight_layout()
        st.pyplot(fig_sudeste)

    # Gráfico para a Região Nordeste
    st.markdown("---")
    st.subheader(f"{nome_var} na Região Nordeste (2020-2025)")
    
    df_nordeste = df_unificado[df_unificado['Regiao'] == 'NORDESTE']
    
    if df_nordeste.empty:
        st.warning("Dados para a Região Nordeste não encontrados.")
    else:
        fig_nordeste, ax_nordeste = plt.subplots(figsize=(10, 6))
        df_ano_nordeste_grouped = df_nordeste.groupby(['Ano', 'Mês'])[coluna_var].mean().unstack(level=0)

        for ano in anos:
            if ano in df_ano_nordeste_grouped.columns:
                ax_nordeste.plot(meses, df_ano_nordeste_grouped[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        
        ax_nordeste.set_title(f'Média Mensal de {nome_var} - Nordeste (2020-2025)')
        ax_nordeste.set_xlabel('Mes')
        ax_nordeste.set_ylabel(nome_var)
        ax_nordeste.set_xticks(meses)
        ax_nordeste.grid(True)
        ax_nordeste.legend(title='Ano')
        plt.tight_layout()
        st.pyplot(fig_nordeste)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro relacionado a uma coluna ausente: '{e}'. Verifique o cabeçalho do CSV.")
except Exception as e:
    st.error(f"Erro inesperado: {e}")
