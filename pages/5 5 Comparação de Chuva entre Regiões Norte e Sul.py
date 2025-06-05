import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# Caminho relativo ao arquivo CSV dentro do projeto
# Certifique-se de que o arquivo 'medias_mensais_geo_2020_2025.csv'
# esteja no subdiretório 'medias' em relação ao script Python.
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Médias Mensais Regionais (2020-2025) - Facetado por Região e Variável")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # Calcular a média da temperatura se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns:
        df_unificado['Temperatura Média (°C)'] = (
            df_unificado['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df_unificado['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    elif 'Temperatura Média (°C)' not in df_unificado.columns:
        pass # A coluna pode já existir ou não ser a selecionada, então não precisa de erro aqui

    # Certificar-se de que a coluna 'Mês' é numérica
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado = df_unificado.dropna(subset=['Mês'])

    # Lista de regiões e anos únicas
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Variáveis a serem plotadas
    variaveis = {
        'Temperatura Média (°C)': 'Temperatura Média (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }

    # Seleção interativa da variável, com 'Precipitação Total (mm)' como padrão
    if 'Precipitação Total (mm)' in variaveis:
        default_var_index = list(variaveis.keys()).index('Precipitação Total (mm)')
    else:
        default_var_index = 0

    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()), index=default_var_index)
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    cmap = plt.get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Gráfico facetado por região
    st.subheader(f"Média Mensal de {nome_var} por Região (2020-2025)")
    
    n_cols = 3
    n_rows = int(np.ceil(len(regioes) / n_cols))
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(5*n_cols, 4*n_rows), sharey=True)
    
    if n_rows * n_cols > 1:
        axes = axes.flatten()
    elif len(regioes) == 1:
        axes = [axes]

    for i, regiao in enumerate(regioes):
        ax = axes[i]
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        for ano in anos:
            df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
            if not df_ano_regiao.empty:
                ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        ax.set_title(regiao)
        ax.set_xlabel('Mês')
        if i % n_cols == 0:
            ax.set_ylabel(nome_var)
        ax.set_xticks(meses)
        ax.grid(True)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    handles, labels = [], []
    for ax_item in axes:
        if ax_item and ax_item.lines:
            handles, labels = ax_item.get_legend_handles_labels()
            if handles:
                break
            
    if handles and labels:
        fig.legend(handles, labels, title='Ano', loc='upper right', bbox_to_anchor=(1.05, 1))

    plt.tight_layout(rect=[0, 0, 0.95, 1])
    st.pyplot(fig)

    # --- Análise de Comparação de Chuva (Norte vs. Sul) ---
    if nome_var == 'Precipitação Total (mm)':
        st.subheader("Comparação de Precipitação: Regiões Norte vs. Sul (2020-2025)")

        # Filtra os dados para as regiões Norte e Sul
        df_norte_sul = df_unificado[df_unificado['Regiao'].isin(['Norte', 'Sul'])]

        # Calcula a precipitação média mensal por região para o período
        precipitacao_media_mensal = df_norte_sul.groupby(['Regiao', 'Mês'])[coluna_var].mean().unstack(level=0)
        
        st.write("### Precipitação Média Mensal (mm) por Região (2020-2025)")
        st.dataframe(precipitacao_media_mensal.round(2))

        st.write("---")
        st.write("### Análise de Volumes, Picos e Secas")

        for regiao in ['Norte', 'Sul']:
            st.markdown(f"#### Região {regiao}")
            if regiao in precipitacao_media_mensal.columns:
                dados_regiao = precipitacao_media_mensal[regiao]
                
                # Volume total (soma das médias mensais, pois a questão fala de volumes)
                volume_total_estimado = dados_regiao.sum() * (len(anos)) # Multiplica pelo número de anos para uma estimativa total
                st.write(f"- **Volume de Precipitação:** O volume médio anual estimado para o período é de aproximadamente **{volume_total_estimado:.2f} mm**.")

                # Mês de pico (mais chuvoso)
                mes_pico = dados_regiao.idxmax()
                valor_pico = dados_regiao.max()
                st.write(f"- **Pico de Chuva:** O mês mais chuvoso é tipicamente **{mes_pico}** (com média de **{valor_pico:.2f} mm**).")

                # Mês de seca (mais seco)
                mes_seca = dados_regiao.idxmin()
                valor_seca = dados_regiao.min()
                st.write(f"- **Período de Seca:** O mês mais seco é tipicamente **{mes_seca}** (com média de **{valor_seca:.2f} mm**).")
            else:
                st.write(f"Dados de precipitação não disponíveis para a Região {regiao}.")

        st.markdown("""
        ---
        ### Justificativa das Diferenças Geográficas e Climáticas

        As diferenças nos regimes de precipitação entre as Regiões Norte e Sul do Brasil são predominantemente explicadas por suas características geográficas e a influência de sistemas climáticos distintos:

        * **Região Norte (Clima Equatorial):**
            * **Proximidade com o Equador:** A Região Norte está localizada em baixas latitudes, próxima à Linha do Equador. Isso a coloca sob a influência da Zona de Convergência Intertropical (ZCIT), um sistema de baixa pressão que atrai massas de ar úmidas e causa chuvas abundantes e bem distribuídas ao longo de quase todo o ano.
            * **Floresta Amazônica:** A vasta cobertura florestal contribui para a umidade atmosférica e o ciclo hidrológico local através da evapotranspiração, realimentando a própria chuva.
            * **Volumes e Picos:** Consequentemente, o Norte apresenta os maiores volumes anuais de precipitação do país, com picos de chuva geralmente no primeiro semestre (entre janeiro e maio), mas com pouca variação de temperatura ao longo do ano. O período "mais seco" ainda tem volumes significativos em comparação com o inverno de outras regiões.

        * **Região Sul (Clima Subtropical):**
            * **Latitude Elevada:** A Região Sul está localizada em latitudes mais altas (abaixo do Trópico de Capricórnio), o que a submete a regimes climáticos diferentes.
            * **Frentes Frias e Ciclones Extratropicais:** A precipitação no Sul é influenciada principalmente pela passagem de frentes frias, que trazem massas de ar polares e causam chuvas bem distribuídas ao longo do ano, sem uma estação seca tão definida quanto em regiões tropicais do Brasil.
            * **Volumes e Picos:** Embora os volumes anuais sejam menores que no Norte, a distribuição é mais regular. Os picos de chuva podem ocorrer em diferentes estações, dependendo da influência de frentes frias ou sistemas convectivos de verão, e o inverno pode ter chuvas mais intensas devido a ciclones extratropicais. As chuvas no inverno são mais frequentes e com volumes significativos, não configurando um período de seca como no Norte.

        Em resumo, enquanto o Norte é dominado por um clima equatorial úmido com chuvas o ano todo devido à ZCIT e à Amazônia, o Sul tem um clima subtropical com chuvas mais regulares devido à influência de frentes frias e sistemas extratropicais.
        """)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e o nome do arquivo.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
