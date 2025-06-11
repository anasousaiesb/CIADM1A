import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np # Importar numpy para cálculos numéricos

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide", page_title="Médias Mensais Regionais 📈")

# CSS para estilização aprimorada do título e subtítulo
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fa; /* Fundo suave para o aplicativo */
}
.main-title-2 {
    font-size: 3.2em;
    font-weight: 700;
    color: #007BFF; /* Um azul vibrante */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle-2 {
    font-size: 1.6em;
    color: #1E90FF; /* Um azul um pouco mais claro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section-2 {
    background-color: #e0f2f7; /* Fundo levemente azul para a seção de cabeçalho */
    padding: 1.5em;
    border-radius: 10px;
    margin-bottom: 2em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

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
    elif 'Temp_Media' not in df_unificado.columns: # Se não tem max/min E não tem Temp_Media, levanta erro
        st.error("Erro: O arquivo CSV não contém a coluna 'Temp_Media' nem as colunas 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' para calcular a temperatura média.")
        st.stop() # Para a execução do script
    # --- FIM DO CÁLCULO DA TEMPERATURA MÉDIA ---

    # Certificar-se de que a coluna 'Mês' é numérica
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado = df_unificado.dropna(subset=['Mês'])

    # --- TÍTULO PRINCIPAL E SUBTÍTULO COM EMOJIS ---
    st.markdown('<div class="header-section-2">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title-2">Médias Mensais Regionais por Variável 📊🌍</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-2">Análise Climática Detalhada (2020-2025) 📈</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.header("Selecione os Parâmetros para Análise 🧐")
    st.markdown("""
        Utilize os seletores abaixo para escolher a **região** e a **variável climática**
        que você deseja visualizar. O gráfico mostrará as tendências mensais ao longo dos anos
        para sua seleção, além de uma linha da média histórica.
        """)

    # Lista de regiões e anos únicas
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())
    meses = sorted(df_unificado['Mês'].unique()) # Garante que os meses estão ordenados corretamente

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

    st.subheader(f"Média Mensal de {nome_var} na Região {regiao_selecionada} (2020-2025) 📉")
    st.markdown("""
        Este gráfico de linhas exibe a **média mensal da variável selecionada** para a região escolhida,
        com cada linha representando um ano diferente. A linha tracejada vermelha indica a
        **média histórica mensal** para toda a série temporal (2020-2025), permitindo uma
        comparação visual rápida das variações anuais em relação ao padrão de longo prazo.
        """)
    fig, ax = plt.subplots(figsize=(10, 6)) # Aumentei um pouco o tamanho do gráfico

    # Dicionário para armazenar os valores anuais médios para análise de desvio
    valores_anuais_por_mes = {}

    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
        if not df_ano_regiao.empty:
            ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
            valores_anuais_por_mes[ano] = df_ano_regiao.values
        else:
            valores_anuais_por_mes[ano] = np.full(len(meses), np.nan) # Preenche com NaN se não houver dados

    # Calcula a média histórica mensal para a variável e região selecionadas
    # Converte o dicionário para um DataFrame para facilitar o cálculo da média
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
    st.markdown("---")
    st.subheader(f"Análise de Variabilidade Anual para {nome_var} na Região {regiao_selecionada} 🔬")
    st.markdown("""
        Esta seção detalha o quão atípico cada ano foi em relação à média histórica mensal para a variável e região selecionadas.
        Um **maior desvio médio absoluto** indica que os valores daquele ano se afastaram mais do padrão usual para os respectivos meses.
        """)

    # Calcula o desvio absoluto médio de cada ano em relação à média histórica mensal
    desvios_absolutos_anuais = {}
    for ano in anos:
        # Pega os valores do ano, ignora NaNs se houver
        valores_ano = df_valores_anuais[ano].dropna()
        media_historica_correspondente = media_historica_mensal[~df_valores_anuais[ano].isna()]

        if not valores_ano.empty:
            # Calcula o desvio mês a mês e então a média dos desvios absolutos
            desvios = np.abs(valores_ano - media_historica_correspondente)
            desvios_absolutos_anuais[ano] = desvios.mean()
        else:
            desvios_absolutos_anuais[ano] = np.nan

    # Identifica o ano mais atípico (maior desvio absoluto médio)
    if desvios_absolutos_anuais:
        # Filtra NaNs para encontrar o máximo
        desvios_validos = {k: v for k, v in desvios_absolutos_anuais.items() if not np.isnan(v)}
        if desvios_validos:
            ano_mais_atipico = max(desvios_validos, key=desvios_validos.get)
            maior_desvio = desvios_validos[ano_mais_atipico]
            
            # Extrair unidade da variável para exibir no texto
            unidade_var = nome_var.split('(')[1].split(')')[0] if '(' in nome_var else ''

            st.write(f"Na Região **{regiao_selecionada}**, para a variável **{nome_var}**: ")
            st.write(f"- O ano de **{ano_mais_atipico}** se destaca como o mais atípico, com um desvio médio de **{maior_desvio:.2f} {unidade_var}** em relação à média histórica mensal (2020-2025).")
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

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Por favor, verifique se o seu CSV possui as colunas esperadas para a variável selecionada ou para o cálculo da temperatura média (TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C) e TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)).")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
