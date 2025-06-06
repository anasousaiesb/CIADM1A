import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Padrões Sazonais de Temperatura (2020-2025) - Identificação de Meses/Anos Atípicos")

# Dicionário para mapear abreviações das regiões
mapa_regioes = {
    "CO": "Centro-Oeste",
    "NE": "Nordeste",
    "N": "Norte",
    "S": "Sul",
    "SE": "Sudeste"
}

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Aplicar o mapeamento de regiões
    df_unificado['Regiao'] = df_unificado['Regiao'].map(mapa_regioes)

    # Lista de regiões disponíveis
    regioes_disponiveis = sorted(df_unificado['Regiao'].dropna().unique())

    # Definir as regiões padrão, garantindo que estão na lista
    regiao_a = st.selectbox("Região A (Padrão: Sul)", regioes_disponiveis, index=0 if "Sul" not in regioes_disponiveis else regioes_disponiveis.index("Sul"))
    regiao_b = st.selectbox("Região B (Padrão: Norte)", regioes_disponiveis, index=1 if "Norte" not in regioes_disponiveis else regioes_disponiveis.index("Norte"))

    # Variável a ser analisada
    coluna_temp = 'Temp_Media'

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('coolwarm')
    anos = sorted(df_unificado['Ano'].unique())
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Criando gráficos separados para cada região
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), sharey=True)

    # Dicionário para armazenar informações para a análise dinâmica
    analise_regioes = {regiao_a: {}, regiao_b: {}}

    for i, regiao in enumerate([regiao_a, regiao_b]):
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        medias_mensais = df_regiao.groupby(['Ano', 'Mês'])[coluna_temp].mean().reset_index()

        # Cálculos para análise dinâmica
        media_geral = medias_mensais[coluna_temp].mean()
        desvio_padrao = medias_mensais[coluna_temp].std()
        limite_superior = media_geral + 1.5 * desvio_padrao
        limite_inferior = media_geral - 1.5 * desvio_padrao
        
        # Armazenar métricas para análise
        analise_regioes[regiao]['media'] = round(media_geral, 1)
        analise_regioes[regiao]['amplitude'] = round(medias_mensais[coluna_temp].max() - medias_mensais[coluna_temp].min(), 1)
        analise_regioes[regiao]['mes_mais_quente'] = medias_mensais.loc[medias_mensais[coluna_temp].idxmax(), 'Mês']
        analise_regioes[regiao]['mes_mais_frio'] = medias_mensais.loc[medias_mensais[coluna_temp].idxmin(), 'Mês']
        analise_regioes[regiao]['num_atipicos'] = len(medias_mensais[(medias_mensais[coluna_temp] > limite_superior) | 
                                                                  (medias_mensais[coluna_temp] < limite_inferior)])

        meses_atipicos = medias_mensais[(medias_mensais[coluna_temp] > limite_superior) | 
                                      (medias_mensais[coluna_temp] < limite_inferior)]

        for ano in anos:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_temp].mean()
            if not df_ano_regiao.empty:
                axes[i].plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', 
                           color=cores_anos[ano], label=f'{ano}')

        axes[i].set_title(f"Temperatura Média - {regiao} (2020-2025)")
        axes[i].set_xlabel("Mês")
        axes[i].set_xticks(range(1, 13))
        axes[i].set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
        axes[i].grid(True)
        axes[i].legend(title="Ano")

    plt.tight_layout()
    st.pyplot(fig)

    # Exibir os meses/anos atípicos
    if not meses_atipicos.empty:
        st.subheader("Meses/Anos Atípicos Identificados")
        st.dataframe(meses_atipicos)

    # Análise dinâmica comparativa
    st.subheader("Análise Comparativa das Regiões Selecionadas")
    
    # Explicação dinâmica baseada nas regiões selecionadas
    st.markdown(f"""
    ### Padrões Sazonais: {regiao_a} vs {regiao_b} (2020-2025)
    
    **{regiao_a}**:
    - Temperatura média anual: {analise_regioes[regiao_a]['media']}°C
    - Amplitude térmica anual: {analise_regioes[regiao_a]['amplitude']}°C
    - Mês tipicamente mais quente: {analise_regioes[regiao_a]['mes_mais_quente']}º mês
    - Mês tipicamente mais frio: {analise_regioes[regiao_a]['mes_mais_frio']}º mês
    - Número de meses atípicos identificados: {analise_regioes[regiao_a]['num_atipicos']}
    
    **{regiao_b}**:
    - Temperatura média anual: {analise_regioes[regiao_b]['media']}°C
    - Amplitude térmica anual: {analise_regioes[regiao_b]['amplitude']}°C
    - Mês tipicamente mais quente: {analise_regioes[regiao_b]['mes_mais_quente']}º mês
    - Mês tipicamente mais frio: {analise_regioes[regiao_b]['mes_mais_frio']}º mês
    - Número de meses atípicos identificados: {analise_regioes[regiao_b]['num_atipicos']}
    
    **Comparativo**:
    - A região {regiao_a if analise_regioes[regiao_a]['amplitude'] > analise_regioes[regiao_b]['amplitude'] else regiao_b} apresenta maior variação sazonal.
    - A região {regiao_a if analise_regioes[regiao_a]['media'] > analise_regioes[regiao_b]['media'] else regiao_b} é geralmente mais quente em média.
    - {regiao_a if analise_regioes[regiao_a]['num_atipicos'] > analise_regioes[regiao_b]['num_atipicos'] else regiao_b} apresenta mais meses com temperaturas atípicas, sugerindo maior variabilidade climática.
    
    **Interpretação**:
    Os gráficos mostram que {regiao_a} e {regiao_b} apresentam padrões sazonais distintos. Enquanto {regiao_a} {f"tem uma sazonalidade mais marcada" if analise_regioes[regiao_a]['amplitude'] > 5 else "mantém temperaturas mais estáveis ao longo do ano"}, {regiao_b} {f"exibe variações mais pronunciadas entre estações" if analise_regioes[regiao_b]['amplitude'] > 5 else "mostra pouca variação entre meses"}. Os meses atípicos identificados podem estar relacionados a eventos climáticos extremos ou mudanças nos padrões atmosféricos.
    """)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
