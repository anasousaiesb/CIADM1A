import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho para o arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Análise Sazonal de Temperatura - Regiões do Brasil (2020-2025)")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado, encoding='latin1')

    # Correção de nomes de colunas se necessário
    df_unificado.rename(columns={'MÃªs': 'Mês'}, inplace=True)
    df_unificado['Regiao'] = df_unificado['Regiao'].astype(str).str.strip().str.upper()

    # Dicionário para mapear nomes completos das regiões
    regioes = {
        "CO": "Centro-Oeste",
        "N": "Norte",
        "NE": "Nordeste",
        "S": "Sul",
        "SE": "Sudeste"
    }

    # Aplicar mapeamento de nomes completos e tratar valores não mapeados
    df_unificado['Regiao_Completa'] = df_unificado['Regiao'].map(regioes)
    
    # Exibir valores únicos para depuração
    st.write("Valores únicos na coluna 'Regiao':", df_unificado['Regiao'].unique())
    st.write("Valores únicos após mapeamento:", df_unificado['Regiao_Completa'].dropna().unique())

    # Certificar que 'Mês' é numérico
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado.dropna(subset=['Mês'], inplace=True)

    # Definir anos e meses únicos
    meses = sorted(df_unificado['Mês'].unique())
    anos = sorted(df_unificado['Ano'].unique())

    # Seleção interativa da região
    regioes_disponiveis = sorted(df_unificado['Regiao_Completa'].dropna().unique())
    if not regioes_disponiveis:
        st.error("Nenhuma região válida encontrada no dataset. Verifique o formato dos dados.")
        st.stop()

    regiao_selecionada = st.selectbox("Selecione a região:", regioes_disponiveis)

    # Filtragem dos dados para a região selecionada
    df_regiao = df_unificado[df_unificado['Regiao_Completa'] == regiao_selecionada]

    if df_regiao.empty:
        st.warning(f"Dados para a região {regiao_selecionada} não encontrados. Verifique os nomes das regiões no CSV.")
    else:
        # Agrupar por mês e calcular média de temperatura
        df_grouped = df_regiao.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)

        # Cores para os anos
        from matplotlib.cm import get_cmap
        cmap = get_cmap('viridis')
        cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

        # Gráfico de temperatura sazonal
        st.subheader(f"Padrões Sazonais de Temperatura - {regiao_selecionada} (2020-2025)")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for ano in anos:
            if ano in df_grouped.columns:
                ax.plot(meses, df_grouped[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        
        ax.set_title(f"Temperatura Média Mensal - {regiao_selecionada} (2020-2025)")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Temperatura Média (°C)")
        ax.set_xticks(meses)
        ax.grid(True)
        ax.legend(title="Ano")
        plt.tight_layout()
        st.pyplot(fig)

        # Identificação de meses/anos atípicos
        st.markdown("---")
        st.subheader("Identificação de Anomalias de Temperatura")
        
        # Calcular média e desvio padrão para cada mês
        df_media_mensal = df_grouped.mean(axis=1)
        df_desvio_mensal = df_grouped.std(axis=1)

        # Destacar meses e anos que desviam muito da média
        anomalias = {}
        for ano in anos:
            if ano in df_grouped.columns:
                desvios = ((df_grouped[ano] - df_media_mensal) / df_desvio_mensal).abs()
                anomalias[ano] = desvios[desvios > 2].index.tolist()  # Considerando desvios acima de 2 sigmas

        if any(anomalias.values()):
            st.write(f"Os seguintes meses apresentaram temperaturas atípicas na região {regiao_selecionada}:")
            for ano, meses_atipicos in anomalias.items():
                if meses_atipicos:
                    st.write(f"- **{ano}**: {', '.join(map(str, meses_atipicos))}")
        else:
            st.write("Nenhuma anomalia significativa identificada.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
