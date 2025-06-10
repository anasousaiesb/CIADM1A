import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# Caminho relativo ao arquivo CSV dentro do projeto
# Ajuste este caminho conforme a localização do seu arquivo medias_mensais_geo_temp_media_completo.csv
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

st.title("Padrões Sazonais Extremos: Amplitude Térmica e Variação de Precipitação")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

    # --- CALCULA A TEMPERATURA MÉDIA SE AS COLUNAS DE MAX/MIN EXISTIREM ---
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df_unificado.columns:
        df_unificado['Temp_Media'] = (
            df_unificado['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
            df_unificado['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']
        ) / 2
    elif 'Temp_Media' not in df_unificado.columns:
        st.error("Erro: O arquivo CSV não contém a coluna 'Temp_Media' nem as colunas 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' para calcular a temperatura média.")
        st.stop()
    # --- FIM DO CÁLCULO DA TEMPERATURA MÉDIA ---

    # Certificar-se de que a coluna 'Mês' é numérica
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado = df_unificado.dropna(subset=['Mês'])

    # Lista de regiões e anos únicas
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique())

    # Seleção interativa da região
    regiao_selecionada = st.selectbox("Selecione a região para visualizar:", regioes)

    # Variáveis a serem plotadas
    variaveis = {
        'Temperatura Média (°C)': 'Temp_Media',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)'
    }

    # Seleção interativa da variável
    nome_var = st.selectbox("Selecione a variável para visualizar:", list(variaveis.keys()))
    coluna_var = variaveis[nome_var]

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # Filtra o DataFrame para a região selecionada
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]

    st.subheader(f"Média Mensal de {nome_var} na Região {regiao_selecionada} (2020-2025)")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Dicionário para armazenar os valores anuais médios para análise de desvio
    valores_anuais_por_mes = {}

    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
        if not df_ano_regiao.empty:
            ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
            valores_anuais_por_mes[ano] = df_ano_regiao.values
        else:
            valores_anuais_por_mes[ano] = np.full(len(meses), np.nan)

    # Calcula a média histórica mensal para a variável e região selecionadas
    df_valores_anuais = pd.DataFrame(valores_anuais_por_mes, index=meses)
    media_historica_mensal = df_valores_anuais.mean(axis=1)

    # Adiciona a linha da média histórica ao gráfico
    ax.plot(meses, media_historica_mensal.values, linestyle='--', color='red', label='Média Histórica (2020-2025)', linewidth=2)

    ax.set_title(f'Média Mensal de {nome_var} - {regiao_selecionada} (2020-2025)')
    ax.set_xlabel('Mês')
    ax.set_ylabel(nome_var)
    ax.set_xticks(meses)
    ax.grid(True)
    ax.legend(title='Ano')
    plt.tight_layout()
    st.pyplot(fig)

    # --- Análise de Variabilidade Anual ---
    st.subheader(f"Análise de Variabilidade Anual para {nome_var} na Região {regiao_selecionada}")

    desvios_absolutos_anuais = {}
    for ano in anos:
        valores_ano = df_valores_anuais[ano].dropna()
        media_historica_correspondente = media_historica_mensal[~df_valores_anuais[ano].isna()]

        if not valores_ano.empty:
            desvios = np.abs(valores_ano - media_historica_correspondente)
            desvios_absolutos_anuais[ano] = desvios.mean()
        else:
            desvios_absolutos_anuais[ano] = np.nan

    if desvios_absolutos_anuais:
        desvios_validos = {k: v for k, v in desvios_absolutos_anuais.items() if not np.isnan(v)}
        if desvios_validos:
            ano_mais_atipico = max(desvios_validos, key=desvios_validos.get)
            maior_desvio = desvios_validos[ano_mais_atipico]

            st.write(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
            st.write(f"- O ano de **{ano_mais_atipico}** se destaca como o mais atípico, com um desvio médio de **{maior_desvio:.2f} {nome_var.split('(')[1].split(')')[0] if '(' in nome_var else ''}** em relação à média histórica mensal (2020-2025).")
            st.write(f"*(Um desvio maior indica que os valores daquele ano se afastaram mais da média para os respectivos meses.)*")

            st.write("\n**Desvios médios anuais em relação à média histórica (quanto maior, mais atípico):**")
            desvios_df = pd.DataFrame.from_dict(desvios_absolutos_anuais, orient='index', columns=['Desvio Médio Absoluto'])
            st.dataframe(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).round(2))

            st.markdown(f"**Implicações:**")
            if nome_var == 'Temperatura Média (°C)':
                st.markdown("- **Temperaturas atipicamente altas:** Podem indicar ondas de calor, impactando a saúde humana, agricultura (estresse hídrico), consumo de energia (ar-condicionado) e ecossistemas. Podem também indicar uma tendência de aquecimento ou um evento climático anômalo como El Niño/La Niña intensos.")
                st.markdown("- **Temperaturas atipicamente baixas:** Podem indicar geadas (prejudiciais à agricultura), maior demanda por aquecimento, e podem estar ligadas a massas de ar frio ou eventos climáticos específicos.")
            elif nome_var == 'Precipitação Total (mm)':
                st.markdown("- **Precipitação atipicamente alta:** Pode causar inundações, deslizamentos de terra, perdas agrícolas (colheitas danificadas), e sobrecarga em infraestruturas de saneamento. Beneficia reservatórios, mas de forma descontrolada pode ser destrutiva.")
                st.markdown("- **Precipitação atipicamente baixa:** Pode levar a secas, escassez hídrica (impactando abastecimento e energia hidrelétrica), incêndios florestais e perdas significativas na agricultura e pecuária. Pode indicar uma situação de estiagem prolongada.")
            elif nome_var == 'Radiação Global (Kj/m²)':
                st.markdown("- **Radiação atipicamente alta:** Pode beneficiar a geração de energia solar, mas também pode indicar dias com menos cobertura de nuvens, possivelmente associados a períodos de seca ou temperaturas elevadas. Importante para o balanço energético da superfície.")
                st.markdown("- **Radiação atipicamente baixa:** Sugere maior nebulosidade ou menor insolação, o que pode impactar a produtividade de culturas que dependem de luz e a eficiência de sistemas solares. Pode estar ligada a períodos chuvosos ou de maior cobertura de nuvens.")
        else:
            st.write("Dados insuficientes para calcular desvios para todos os anos.")
    else:
        st.write("Não há dados suficientes para realizar a análise de variabilidade anual.")

    # --- NOVO CÁLCULO: IDENTIFICAÇÃO DE EXTREMOS SAZONAIS ---
    st.subheader("Padrões Sazonais Extremos: Amplitude Térmica e Variação de Precipitação")

    # Inicializa variáveis para armazenar os máximos globais
    max_amplitude_termica = -np.inf
    regiao_maior_amplitude_termica = ""

    max_variacao_precipitacao = -np.inf
    regiao_maior_variacao_precipitacao = ""

    # Dicionários para armazenar os resultados por região
    amplitude_termica_por_regiao = {}
    variacao_precipitacao_por_regiao = {}

    # Itera sobre cada região para calcular as métricas de extremos
    for regiao in regioes:
        df_temp_regiao = df_unificado[df_unificado['Regiao'] == regiao]

        # 1. Amplitude Térmica (Temperatura Média)
        if 'Temp_Media' in df_temp_regiao.columns and not df_temp_regiao['Temp_Media'].isnull().all():
            # Calcula a média mensal de Temp_Media para a região ao longo de todos os anos
            media_mensal_temp = df_temp_regiao.groupby('Mês')['Temp_Media'].mean()
            # A amplitude térmica mensal é a diferença entre a máxima e a mínima média mensal
            amplitude_regiao = media_mensal_temp.max() - media_mensal_temp.min()
            amplitude_termica_por_regiao[regiao] = amplitude_regiao

            if amplitude_regiao > max_amplitude_termica:
                max_amplitude_termica = amplitude_regiao
                regiao_maior_amplitude_termica = regiao

        # 2. Variação de Precipitação Mensal
        if 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' in df_temp_regiao.columns and not df_temp_regiao['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].isnull().all():
            # Calcula o desvio padrão da precipitação mensal para cada mês ao longo dos anos
            # A variação é representada pelo desvio padrão das médias mensais de precipitação
            media_mensal_precipitacao = df_temp_regiao.groupby('Mês')['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].mean()
            variacao_regiao = media_mensal_precipitacao.std() # Usando desvio padrão das médias mensais como variação
            variacao_precipitacao_por_regiao[regiao] = variacao_regiao

            if variacao_regiao > max_variacao_precipitacao:
                max_variacao_precipitacao = variacao_regiao
                regiao_maior_variacao_precipitacao = regiao

    st.write("---") # Separador visual

    if regiao_maior_amplitude_termica:
        st.markdown(f"**Região com Maior Amplitude Térmica Média (2020-2025):**")
        st.markdown(f"- A região **{regiao_maior_amplitude_termica}** apresenta a maior amplitude térmica média, com uma diferença de **{max_amplitude_termica:.2f} °C** entre o mês mais quente e o mais frio (com base nas médias mensais históricas).")
        st.markdown("  *Isso indica que essa região experimenta variações mais drásticas de temperatura entre as estações.*")
        st.write("Como isso aparece no gráfico de **Temperatura Média**:")
        st.markdown("- As curvas de temperatura para esta região (quando selecionada) exibirão **picos e vales mais acentuados e distantes entre si** ao longo do ano, especialmente na linha da 'Média Histórica'. Isso significa que os meses de verão são consideravelmente mais quentes e os meses de inverno são notavelmente mais frios em comparação com outras regiões.")

    if regiao_maior_variacao_precipitacao:
        st.markdown(f"**Região com Maior Variação de Precipitação Mensal Média (2020-2025):**")
        st.markdown(f"- A região **{regiao_maior_variacao_precipitacao}** demonstra a maior variação de precipitação mensal (medida pelo desvio padrão das médias mensais), indicando uma **maior irregularidade no regime de chuvas**. O desvio padrão é de **{max_variacao_precipitacao:.2f} mm**.")
        st.markdown("  *Isso sugere que essa região pode ter períodos de seca e chuva intensa mais marcantes.*")
        st.write("Como isso aparece no gráfico de **Precipitação Total**:")
        st.markdown("- As curvas de precipitação para esta região (quando selecionada) mostrarão **flutuações mais dramáticas** ao longo do ano. Você observará meses com volumes de chuva muito elevados (picos) seguidos por meses com volumes muito baixos, ou quase nulos (vales), evidenciando a natureza mais irregular e extrema do regime de precipitação sazonal.")
    st.write("---") # Separador visual


except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média (TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C) e TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)).")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
