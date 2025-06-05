import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho para o arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Análise Comparativa de Temperatura - Regiões do Brasil (2020-2025)")

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

    # Seleção interativa das regiões
    regioes_disponiveis = sorted(df_unificado['Regiao_Completa'].dropna().unique())

    if len(regioes_disponiveis) < 2:
        st.error("É necessário pelo menos duas regiões válidas no dataset. Verifique o formato dos dados.")
        st.stop()

    regiao1_selecionada = st.selectbox("Selecione a primeira região:", regioes_disponiveis)
    regiao2_selecionada = st.selectbox("Selecione a segunda região:", regioes_disponiveis)

    # Filtragem dos dados para cada região selecionada
    df_regiao1 = df_unificado[df_unificado['Regiao_Completa'] == regiao1_selecionada]
    df_regiao2 = df_unificado[df_unificado['Regiao_Completa'] == regiao2_selecionada]

    if df_regiao1.empty or df_regiao2.empty:
        st.warning("Dados não encontrados para uma ou ambas as regiões selecionadas. Verifique os nomes das regiões no CSV.")
    else:
        # Agrupar por mês e calcular média de temperatura
        df_grouped1 = df_regiao1.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)
        df_grouped2 = df_regiao2.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)

        # Cores para os anos
        from matplotlib.cm import get_cmap
        cmap = get_cmap('viridis')
        cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

        # Gerar gráficos para comparação das regiões selecionadas
        st.subheader(f"Padrões Sazonais - {regiao1_selecionada} vs {regiao2_selecionada} (2020-2025)")
        
        fig, axs = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

        for ano in anos:
            if ano in df_grouped1.columns:
                axs[0].plot(meses, df_grouped1[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
            if ano in df_grouped2.columns:
                axs[1].plot(meses, df_grouped2[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))

        axs[0].set_title(f"Temperatura Média Mensal - {regiao1_selecionada}")
        axs[0].set_ylabel("Temperatura Média (°C)")
        axs[0].grid(True)
        axs[0].legend(title="Ano")

        axs[1].set_title(f"Temperatura Média Mensal - {regiao2_selecionada}")
        axs[1].set_xlabel("Mês")
        axs[1].set_ylabel("Temperatura Média (°C)")
        axs[1].grid(True)
        axs[1].legend(title="Ano")

        plt.tight_layout()
        st.pyplot(fig)

        # **Comparação Sudeste vs Nordeste**
        st.markdown("---")
        st.subheader("Análise Comparativa: Sudeste vs Nordeste (2020-2025)")

        df_sudeste = df_unificado[df_unificado['Regiao_Completa'] == "Sudeste"]
        df_nordeste = df_unificado[df_unificado['Regiao_Completa'] == "Nordeste"]

        if df_sudeste.empty or df_nordeste.empty:
            st.warning("Dados insuficientes para a comparação entre Sudeste e Nordeste.")
        else:
            df_grouped_sudeste = df_sudeste.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)
            df_grouped_nordeste = df_nordeste.groupby(['Ano', 'Mês'])['Temp_Media'].mean().unstack(level=0)

            fig_comp, ax_comp = plt.subplots(figsize=(10, 6))
            
            for ano in anos:
                if ano in df_grouped_sudeste.columns:
                    ax_comp.plot(meses, df_grouped_sudeste[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=f"Sudeste {ano}")
                if ano in df_grouped_nordeste.columns:
                    ax_comp.plot(meses, df_grouped_nordeste[ano].reindex(meses).values, marker='s', linestyle='--', color=cores_anos[ano], label=f"Nordeste {ano}")

            ax_comp.set_title("Comparação de Temperatura - Sudeste vs Nordeste")
            ax_comp.set_xlabel("Mês")
            ax_comp.set_ylabel("Temperatura Média (°C)")
            ax_comp.grid(True)
            ax_comp.legend(title="Região e Ano")
            plt.tight_layout()
            st.pyplot(fig_comp)

            # **Identificação de meses/anos atípicos**
            st.subheader("Identificação de Anomalias de Temperatura")
            
            df_media_mensal_sudeste = df_grouped_sudeste.mean(axis=1)
            df_desvio_mensal_sudeste = df_grouped_sudeste.std(axis=1)

            df_media_mensal_nordeste = df_grouped_nordeste.mean(axis=1)
            df_desvio_mensal_nordeste = df_grouped_nordeste.std(axis=1)

            anomalias_sudeste = {ano: ((df_grouped_sudeste[ano] - df_media_mensal_sudeste) / df_desvio_mensal_sudeste).abs()[((df_grouped_sudeste[ano] - df_media_mensal_sudeste) / df_desvio_mensal_sudeste).abs() > 2].index.tolist() for ano in anos if ano in df_grouped_sudeste.columns}
            
            anomalias_nordeste = {ano: ((df_grouped_nordeste[ano] - df_media_mensal_nordeste) / df_desvio_mensal_nordeste).abs()[((df_grouped_nordeste[ano] - df_media_mensal_nordeste) / df_desvio_mensal_nordeste).abs() > 2].index.tolist() for ano in anos if ano in df_grouped_nordeste.columns}

            st.write("Sudeste - Meses atípicos:", anomalias_sudeste)
            st.write("Nordeste - Meses atípicos:", anomalias_nordeste)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except Exception as e:
    st.error(f"Ocorreu um erro: {e}")
