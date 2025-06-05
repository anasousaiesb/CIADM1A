import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Padrões Sazonais de Temperatura (2020-2025) - Identificação de Meses/Anos Atípicos")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Lista de regiões e anos únicas
    regioes_disponiveis = sorted(df_unificado['Regiao'].unique())

    # Sempre carregar as regiões Sul e Norte
    regioes_padrao = ['Sul', 'Norte']

    # Adicionar opção para escolha de outra região
    regiao_selecionada = st.selectbox("Selecione uma região adicional para análise:", regioes_disponiveis)

    # Variável a ser analisada
    coluna_temp = 'Temp_Media'

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('coolwarm')
    anos = sorted(df_unificado['Ano'].unique())
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)]

    # Criando gráficos separados para cada região
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), sharey=True)

    for i, regiao in enumerate(regioes_padrao + [regiao_selecionada]):
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        medias_mensais = df_regiao.groupby(['Ano', 'Mês'])[coluna_temp].mean().reset_index()

        # Identificação de meses/anos atípicos
        media_geral = medias_mensais[coluna_temp].mean()
        desvio_padrao = medias_mensais[coluna_temp].std()
        limite_superior = media_geral + 1.5 * desvio_padrao
        limite_inferior = media_geral - 1.5 * desvio_padrao

        meses_atipicos = medias_mensais[(medias_mensais[coluna_temp] > limite_superior) | (medias_mensais[coluna_temp] < limite_inferior)]

        for ano in anos:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_temp].mean()
            if not df_ano_regiao.empty:
                axes[i].plot(df_ano_regiao.index, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=f'{ano}')

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

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
