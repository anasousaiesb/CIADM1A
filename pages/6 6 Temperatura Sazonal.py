import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho para o arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Comparação Sazonal de Temperatura - Regiões do Brasil (2020-2025)")

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

    # Certificar que 'Mês' é numérico
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado.dropna(subset=['Mês'], inplace=True)

    # Definir anos e meses únicos
    meses = sorted(df_unificado['Mês'].unique())
    anos = sorted(df_unificado['Ano'].unique())

    # Seleção interativa de duas regiões
    regioes_disponiveis = sorted(df_unificado['Regiao_Completa'].dropna().unique())

    if len(regioes_disponiveis) < 2:
        st.error("É necessário pelo menos duas regiões válidas no dataset. Verifique o formato dos dados.")
        st.stop()

    regiao_A = st.selectbox("Selecione a primeira região:", regioes_disponiveis)
    regiao_B = st.selectbox("Selecione a segunda região:", regioes_disponiveis)

    # Filtragem dos dados para cada região selecionada
    df_regiao_A = df_unificado[df_unificado['Regiao_Completa'] == regiao_A]
    df_regiao_B = df_unificado[df_unificado['Regiao_Completa'] == regiao_B]

    if df_regiao_A.empty or df_regiao_B.empty:
        st.warning("Dados não encontrados para uma ou ambas as regiões selecionadas. Verifique os nomes das regiões no CSV.")
    else:
        # Agrupar por mês e calcular média de temperatura
        df_grouped_A = df_regiao_A.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)
        df_grouped_B = df_regiao_B.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)

        # Cores para os anos
        from matplotlib.cm import get_cmap
        cmap = get_cmap('viridis')
        cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

        # Gerar gráficos para comparação das regiões selecionadas
        st.subheader(f"Padrões Sazonais - {regiao_A} vs {regiao_B} (2020-2025)")
        
        fig, axs = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

        for ano in anos:
            if ano in df_grouped_A.columns:
                axs[0].plot(meses, df_grouped_A[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
            if ano in df_grouped_B.columns:
                axs[1].plot(meses, df_grouped_B[ano].reindex(meses).values, marker='s', linestyle='--', color=cores_anos[ano], label=str(ano))

        axs[0].set_title(f"Temperatura Média Mensal - {regiao_A}")
        axs[0].set_ylabel("Temperatura Média (°C)")
        axs[0].grid(True)
        axs[0].legend(title="Ano")

        axs[1].set_title(f"Temperatura Média Mensal - {regiao_B}")
        axs[1].set_xlabel("Mês")
        axs[1].set_ylabel("Temperatura Média (°C)")
        axs[1].grid(True)
        axs[1].legend(title="Ano")

        plt.tight_layout()
        st.pyplot(fig)

        # **Comparação e Identificação de Anomalias**
        st.markdown("---")
        st.subheader(f"Análise Comparativa: {regiao_A} vs {regiao_B}")

        df_media_mensal_A = df_grouped_A.mean(axis=1)
        df_desvio_mensal_A = df_grouped_A.std(axis=1)

        df_media_mensal_B = df_grouped_B.mean(axis=1)
        df_desvio_mensal_B = df_grouped_B.std(axis=1)

        # **Correção para garantir compatibilidade com JSON**
        anomalias_A = {
            str(ano): [int(mes) for mes in ((df_grouped_A[ano] - df_media_mensal_A) / df_desvio_mensal_A).abs()
                      [((df_grouped_A[ano] - df_media_mensal_A) / df_desvio_mensal_A).abs() > 2].index.tolist()]
            for ano in anos if ano in df_grouped_A.columns
        }

        anomalias_B = {
            str(ano): [int(mes) for mes in ((df_grouped_B[ano] - df_media_mensal_B) / df_desvio_mensal_B).abs()
                      [((df_grouped_B[ano] - df_media_mensal_B) / df_desvio_mensal_B).abs() > 2].index.tolist()]
            for ano in anos if ano in df_grouped_B.columns
        }

        st.write(f"Meses atípicos em {regiao_A}:", anomalias_A)
        st.write(f"Meses atípicos em {regiao_B}:", anomalias_B)

        # **Resumo da Comparação**
        st.markdown("### Principais Diferenças:")
        st.write(f"✅ **{regiao_A}:** Possui padrões de temperatura com estações bem definidas? Apresenta grandes variações ao longo dos meses?")
        st.write(f"✅ **{regiao_B}:** Mantém temperaturas mais constantes? Apresenta períodos de anomalias climáticas?")
        st.write("👀 Compare os gráficos acima e veja como as tendências de temperatura mudam entre as regiões ao longo dos anos.")

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")
