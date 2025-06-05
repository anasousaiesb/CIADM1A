import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np

# Caminho relativo ao arquivo CSV dentro do projeto
# Ajuste este caminho conforme a localização do seu arquivo medias_mensais_geo_temp_media_completo.csv
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

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
            st.write(f"- O ano de **{ano_mais_atipico}** destaca-se como o mais atípico, com um desvio médio de **{maior_desvio:.2f} {nome_var.split('(')[1].split(')')[0] if '(' in nome_var else ''}** em relação à média histórica mensal (2020-2025).")
            st.write(f"*(Um desvio maior indica que os valores daquele ano se afastaram mais da média para os respectivos meses.)*")

            st.write("\n**Desvios médios anuais em relação à média histórica (quanto maior, mais atípico):**")
            desvios_df = pd.DataFrame.from_dict(desvios_absolutos_anuais, orient='index', columns=['Desvio Médio Absoluto'])
            st.dataframe(desvios_df.sort_values(by='Desvio Médio Absoluto', ascending=False).round(2))

            st.markdown(f"**Implicações:**")
            if nome_var == 'Temperatura Média (°C)':
                st.markdown("- **Temperaturas atipicamente altas:** Podem indicar ondas de calor, impactando a saúde humana, agricultura (estresse hídrico), consumo de energia (ar-condicionado) e ecossistemas. Podem também indicar uma tendência de aquecimento ou um evento climático anómalo como El Niño/La Niña intensos.")
                st.markdown("- **Temperaturas atipicamente baixas:** Podem indicar geadas (prejudiciais à agricultura), maior procura por aquecimento, e podem estar ligadas a massas de ar frio ou eventos climáticos específicos.")
            elif nome_var == 'Precipitação Total (mm)':
                st.markdown("- **Precipitação atipicamente alta:** Pode causar inundações, deslizamentos de terra, perdas agrícolas (colheitas danificadas), e sobrecarga em infraestruturas de saneamento. Beneficia reservatórios, mas de forma descontrolada pode ser destrutiva.")
                st.markdown("- **Precipitação atipicamente baixa:** Pode levar a secas, escassez hídrica (impactando abastecimento e energia hidroelétrica), incêndios florestais e perdas significativas na agricultura e pecuária. Pode indicar uma situação de estiagem prolongada.")
            elif nome_var == 'Radiação Global (Kj/m²)':
                st.markdown("- **Radiação atipicamente alta:** Pode beneficiar a geração de energia solar, mas também pode indicar dias com menos cobertura de nuvens, possivelmente associados a períodos de seca ou temperaturas elevadas. Importante para o balanço energético da superfície.")
                st.markdown("- **Radiação atipicamente baixa:** Sugere maior nebulosidade ou menor insolação, o que pode impactar a produtividade de culturas que dependem de luz e a eficiência de sistemas solares. Pode estar ligada a períodos chuvosos ou de maior cobertura de nuvens.")
        else:
            st.write("Dados insuficientes para calcular desvios para todos os anos.")
    else:
        st.write("Não há dados suficientes para realizar a análise de variabilidade anual.")

    st.write("---") # Separador visual

    # --- IDENTIFICAÇÃO DE EXTREMOS SAZONAIS GLOBAIS ---
    st.subheader("Identificação de Padrões Sazonais Extremos (2020-2025)")

    max_amplitude_termica = -np.inf
    regiao_maior_amplitude_termica = ""
    max_variacao_precipitacao = -np.inf
    regiao_maior_variacao_precipitacao = ""

    amplitude_termica_por_regiao = {}
    variacao_precipitacao_por_regiao = {}

    for regiao in regioes:
        df_temp_regiao = df_unificado[df_unificado['Regiao'] == regiao]

        # 1. Amplitude Térmica (Temperatura Média)
        if 'Temp_Media' in df_temp_regiao.columns and not df_temp_regiao['Temp_Media'].isnull().all():
            media_mensal_temp = df_temp_regiao.groupby('Mês')['Temp_Media'].mean()
            amplitude_regiao = media_mensal_temp.max() - media_mensal_temp.min()
            amplitude_termica_por_regiao[regiao] = amplitude_regiao
            if amplitude_regiao > max_amplitude_termica:
                max_amplitude_termica = amplitude_regiao
                regiao_maior_amplitude_termica = regiao

        # 2. Variação de Precipitação Mensal (Desvio Padrão das médias mensais)
        if 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)' in df_temp_regiao.columns and not df_temp_regiao['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].isnull().all():
            media_mensal_precipitacao = df_temp_regiao.groupby('Mês')['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].mean()
            variacao_regiao = media_mensal_precipitacao.std()
            variacao_precipitacao_por_regiao[regiao] = variacao_regiao
            if variacao_regiao > max_variacao_precipitacao:
                max_variacao_precipitacao = variacao_regiao
                regiao_maior_variacao_precipitacao = regiao

    if regiao_maior_amplitude_termica:
        st.markdown(f"**Região com Maior Amplitude Térmica Média (2020-2025):**")
        st.markdown(f"- A região **{regiao_maior_amplitude_termica}** apresenta a maior amplitude térmica média de **{max_amplitude_termica:.2f} °C**.")
        st.markdown("  *Isso indica que essa região experimenta variações mais drásticas de temperatura entre as estações (verões quentes, invernos frios).*")
        st.write("Como isso aparece no gráfico de **Temperatura Média**:")
        st.markdown("- As curvas de temperatura para esta região (quando selecionada) exibirão **picos e vales mais acentuados e distantes entre si** ao longo do ano, especialmente na linha da 'Média Histórica'.")

    if regiao_maior_variacao_precipitacao:
        st.markdown(f"**Região com Maior Variação de Precipitação Mensal Média (2020-2025):**")
        st.markdown(f"- A região **{regiao_maior_variacao_precipitacao}** demonstra a maior variação de precipitação mensal, com um desvio padrão de **{max_variacao_precipitacao:.2f} mm**.")
        st.markdown("  *Isso sugere que essa região pode ter períodos de seca e chuva intensa mais marcantes.*")
        st.write("Como isso aparece no gráfico de **Precipitação Total**:")
        st.markdown("- As curvas de precipitação para esta região (quando selecionada) mostrarão **flutuações mais dramáticas** ao longo do ano (picos de chuva muito altos e vales muito baixos).")
    st.write("---") # Separador visual


    # --- COMPARAÇÃO DE CHUVA ENTRE NORTE E SUL ---
    st.subheader("Comparação de Regimes de Precipitação: Região Norte vs. Região Sul (2020-2025)")

    # Filtra dados para as regiões Norte e Sul
    df_norte_prec = df_unificado[df_unificado['Regiao'] == 'Norte']
    df_sul_prec = df_unificado[df_unificado['Regiao'] == 'Sul']

    # Calcula a média mensal de precipitação para cada região
    media_mensal_norte = df_norte_prec.groupby('Mês')['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].mean().reindex(meses)
    media_mensal_sul = df_sul_prec.groupby('Mês')['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].mean().reindex(meses)

    if not media_mensal_norte.empty and not media_mensal_sul.empty:
        fig_comp_prec, ax_comp_prec = plt.subplots(figsize=(12, 7))
        ax_comp_prec.plot(meses, media_mensal_norte.values, marker='o', linestyle='-', color='blue', label='Região Norte')
        ax_comp_prec.plot(meses, media_mensal_sul.values, marker='o', linestyle='-', color='green', label='Região Sul')

        ax_comp_prec.set_title('Média Mensal de Precipitação: Região Norte vs. Região Sul (2020-2025)')
        ax_comp_prec.set_xlabel('Mês')
        ax_comp_prec.set_ylabel('Precipitação Total (mm)')
        ax_comp_prec.set_xticks(meses)
        ax_comp_prec.grid(True)
        ax_comp_prec.legend()
        plt.tight_layout()
        st.pyplot(fig_comp_prec)

        st.markdown("### Análise das Diferenças nos Regimes de Precipitação:")

        st.markdown(
            "#### Região Norte (Principalmente Amazónia):"
            "\n- **Volumes de Chuva:** Geralmente apresenta volumes de precipitação muito mais elevados durante a maior parte do ano, com um pico claro na estação chuvosa (tipicamente de Dezembro a Maio)."
            "\n- **Picos/Secas:** O regime é caracterizado por uma estação chuvosa prolongada e intensa e uma estação "
            "menos chuvosa (por vezes chamada de \"verão amazónico\") mas que raramente é uma seca completa. "
            "A precipitação é influenciada pela Zona de Convergência Intertropical (ZCIT) e pela humidade "
            "trazida pela Floresta Amazónica."
            "\n- **No Gráfico:** A linha azul ('Região Norte') deverá apresentar valores consistentemente mais altos e um "
            "pico bem definido nos meses de verão/outono do Hemisfério Sul (Dezembro a Maio), com uma redução "
            "menos acentuada nos meses de inverno (Junho a Novembro)."
        )

        st.markdown(
            "#### Região Sul (Clima Subtropical):"
            "\n- **Volumes de Chuva:** Apresenta volumes anuais significativos, mas com uma distribuição mais "
            "uniforme ao longo do ano, sem uma estação de seca tão definida quanto em outras regiões do Brasil. "
            "No entanto, pode haver flutuações e eventos extremos de seca ou excesso de chuva."
            "\n- **Picos/Secas:** A precipitação é influenciada principalmente pela passagem de frentes frias e "
            "sistemas extratropicais. Os meses de verão (Dezembro a Março) podem ter chuvas convectivas "
            "intensas, enquanto no inverno (Junho a Agosto) as chuvas frontais são mais comuns. Pode haver "
            "períodos de seca ou excesso de chuva dependendo da atuação de fenómenos como El Niño ou La Niña."
            "\n- **No Gráfico:** A linha verde ('Região Sul') deverá mostrar valores mais equilibrados ao longo dos meses, "
            "sem um pico tão pronunciado como na Região Norte, e potencialmente com variações mais irregulares "
            "devido à influência de frentes frias."
        )

        st.markdown(
            "### Justificativa das Diferenças:"
            "\n- **Fatores Climáticos:** A Região Norte está sob forte influência da Floresta Amazónica, que contribui "
            "para a humidade e formação de chuvas, e da ZCIT, que atua diretamente sobre a região em certos períodos. "
            "Já a Região Sul é dominada por sistemas meteorológicos de latitudes médias, como as frentes frias, "
            "que trazem chuva de forma mais distribuída e influenciada por massas de ar polares no inverno."
            "\n- **Topografia e Correntes Oceânicas:** Embora não diretamente visíveis nos dados, a topografia e a "
            "proximidade com correntes oceânicas quentes (Norte) e frias (Sul) também desempenham um papel na "
            "distribuição e intensidade da precipitação em cada região."
        )
    else:
        st.write("Dados de precipitação insuficientes para as regiões Norte ou Sul para realizar a comparação.")

    st.write("---") # Separador visual

    # --- NOVO CÁLCULO: TEMPERATURA SAZONAL SUDESTE VS NORDESTE ---
    st.subheader("Padrões Sazonais de Temperatura: Região Sudeste vs. Região Nordeste (2020-2025)")

    # Filtra dados para as regiões Sudeste e Nordeste
    df_sudeste_temp = df_unificado[df_unificado['Regiao'] == 'Sudeste']
    df_nordeste_temp = df_unificado[df_unificado['Regiao'] == 'Nordeste']

    # Calcula a média mensal de temperatura para cada região
    media_mensal_sudeste = df_sudeste_temp.groupby('Mês')['Temp_Media'].mean().reindex(meses)
    media_mensal_nordeste = df_nordeste_temp.groupby('Mês')['Temp_Media'].mean().reindex(meses)

    if not media_mensal_sudeste.empty and not media_mensal_nordeste.empty:
        fig_comp_temp, ax_comp_temp = plt.subplots(figsize=(12, 7))
        ax_comp_temp.plot(meses, media_mensal_sudeste.values, marker='o', linestyle='-', color='purple', label='Região Sudeste')
        ax_comp_temp.plot(meses, media_mensal_nordeste.values, marker='o', linestyle='-', color='orange', label='Região Nordeste')

        ax_comp_temp.set_title('Média Mensal de Temperatura Média: Região Sudeste vs. Região Nordeste (2020-2025)')
        ax_comp_temp.set_xlabel('Mês')
        ax_comp_temp.set_ylabel('Temperatura Média (°C)')
        ax_comp_temp.set_xticks(meses)
        ax_comp_temp.grid(True)
        ax_comp_temp.legend()
        plt.tight_layout()
        st.pyplot(fig_comp_temp)

        st.markdown("### Análise dos Padrões Sazonais de Temperatura:")

        st.markdown(
            "#### Região Sudeste (Clima Subtropical e Tropical):"
            "\n- **Padrão Sazonal Típico:** A Região Sudeste apresenta um padrão sazonal de temperatura bem definido, com verões quentes e chuvosos (Dezembro a Março) e invernos mais amenos e secos (Junho a Agosto). A amplitude térmica é maior que no Nordeste, especialmente em áreas mais continentais."
            "\n- **Identificação de Meses/Anos Atípicos:**"
            "\n  - **Meses mais quentes/frios que o normal:** Olhe para o gráfico de comparação. Se a linha roxa ('Região Sudeste') se desviar significativamente acima ou abaixo da sua média esperada para um determinado mês, isso pode indicar um mês atípico (por exemplo, um inverno mais quente ou um verão mais frio)."
            "\n  - **Anos Atípicos (visual no gráfico geral):** Observe o gráfico de 'Média Mensal de Temperatura Média na Região Sudeste (2020-2025)' (selecionando 'Sudeste' e 'Temperatura Média' nas caixas de seleção). Se uma linha de um ano específico (ex: 2023) estiver consistentemente acima ou abaixo das outras linhas para a maioria dos meses, esse ano pode ser considerado atípico. A seção 'Análise de Variabilidade Anual' para o Sudeste também indicará o ano com maior desvio médio absoluto para a temperatura."
        )

        st.markdown(
            "#### Região Nordeste (Clima Tropical e Semiárido):"
            "\n- **Padrão Sazonal Típico:** A Região Nordeste, por sua vez, tem temperaturas mais elevadas e constantes ao longo do ano devido à sua proximidade com o Equador. A variação sazonal de temperatura é menor. As estações são mais definidas pela precipitação do que pela temperatura."
            "\n- **Identificação de Meses/Anos Atípicos:**"
            "\n  - **Meses mais quentes/frios que o normal:** No gráfico de comparação, se a linha laranja ('Região Nordeste') mostrar quedas ou aumentos incomuns para um mês, isso seria atípico para a região, que tende a ter temperaturas mais estáveis."
            "\n  - **Anos Atípicos (visual no gráfico geral):** Similarmente, observe o gráfico de 'Média Mensal de Temperatura Média na Região Nordeste (2020-2025)'. Anos onde a linha se desvia substancialmente da média histórica para vários meses consecutivos seriam considerados atípicos. A análise de variabilidade anual para o Nordeste também será útil aqui."
        )

        st.markdown(
            "### Justificativa das Diferenças e Atipicidades:"
            "\n- **Latitude e Insolação:** O Nordeste, por estar mais próximo da Linha do Equador, recebe maior e mais constante insolação ao longo do ano, resultando em temperaturas médias mais elevadas e menor amplitude térmica sazonal. O Sudeste, em latitudes mais subtropicais, tem uma variação mais acentuada de insolação entre o verão e o inverno."
            "\n- **Sistemas Climáticos:** O Sudeste é mais influenciado por massas de ar polar no inverno, que podem causar quedas significativas de temperatura, e por sistemas de alta pressão que levam a períodos secos. O Nordeste é mais influenciado por sistemas tropicais, como a Zona de Convergência Intertropical (ZCIT) e os ventos alísios, que mantêm as temperaturas elevadas e a umidade em certas épocas."
            "\n- **Eventos Anômalos (El Niño/La Niña):** Meses e anos atípicos podem ser justificados pela atuação de fenómenos de grande escala, como El Niño (que geralmente causa secas e temperaturas mais altas no Norte e Nordeste e chuvas irregulares no Sul) e La Niña (que pode intensificar chuvas no Norte e Nordeste e causar secas no Sul). Ondas de calor ou de frio intensas também podem gerar atipicidades localizadas."
        )
    else:
        st.write("Dados de temperatura insuficientes para as regiões Sudeste ou Nordeste para realizar a comparação.")


except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média (TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C) e TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)).")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
