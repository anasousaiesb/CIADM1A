import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide", page_title="Contraste Climático Brasil 🌡️💧")

# CSS para estilização aprimorada
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Merriweather', serif; /* Fonte elegante e legível */
    color: #2F4F4F; /* Azul petróleo escuro para o texto */
}

.stApp {
    background: linear-gradient(to right top, #E8F5E9, #FFFFFF); /* Gradiente verde claro para branco */
}

.main-title-6 {
    font-size: 3.5em; /* Tamanho do título principal */
    font-weight: 700;
    color: #0A6640; /* Verde escuro impactante */
    text-align: center;
    margin-bottom: 0.3em;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.15);
    letter-spacing: 0.5px;
}
.subtitle-6 {
    font-size: 1.8em;
    color: #388E3C; /* Verde mais claro para o subtítulo */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 2em;
    font-weight: 400;
    font-style: italic;
}
.header-section-6 {
    background: linear-gradient(135deg, #A5D6A7 0%, #81C784 100%); /* Gradiente verde suave para o cabeçalho */
    padding: 2.5em;
    border-radius: 20px;
    margin-bottom: 2.5em;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    border: 2px solid #66BB6A;
}

.stSidebar .stSelectbox {
    font-weight: 600;
    color: #0A6640;
}

h2 {
    color: #0A6640;
    border-bottom: 2px solid #C8E6C9;
    padding-bottom: 0.5em;
    margin-top: 2.5em;
}

h3 {
    color: #388E3C; /* Verde médio para sub-subtítulos */
    margin-top: 1.5em;
    margin-bottom: 0.8em;
}

.stInfo {
    background-color: #E8F5E9; /* Fundo verde clarinho para info */
    border-left: 5px solid #66BB6A;
    padding: 1em;
    border-radius: 8px;
}

.stWarning {
    background-color: #FFFDE7; /* Amarelo muito claro para warning */
    border-left: 5px solid #FFD54F; /* Amarelo mais vibrante */
    padding: 1em;
    border-radius: 8px;
}

.stMarkdown p {
    line-height: 1.6; /* Aumenta a legibilidade do texto */
}

.stPlotlyChart {
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)
    
    # Calcula a Temp_Media se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] + 
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    elif 'Temp_Media' not in df.columns:
        pass # O erro será tratado no bloco principal

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    
    # Garante que as colunas necessárias existem
    required_cols = ['Temp_Media', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)', 'Regiao', 'Mês', 'Ano']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Erro Crítico: A coluna obrigatória '{col}' não foi encontrada no arquivo CSV. Por favor, verifique seu arquivo e tente novamente. 🛑")
            st.stop()

    df = df.dropna(subset=['Mês', 'Ano'] + required_cols)
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia
    if 'Temp_Media' not in df_unificado.columns:
        st.error("Erro Crítico: A coluna 'Temp_Media' não existe e não pôde ser calculada a partir das colunas de máxima e mínima. Certifique-se de que seu arquivo CSV contém 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'. 🌡️❌")
        st.stop()

    # --- TÍTULO PRINCIPAL ATRAENTE ---
    st.markdown('<div class="header-section-6">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title-6">Contrastando o Clima: Padrões de Temperatura e Precipitação no Brasil 🌡️💧</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-6">Uma Viagem Comparativa entre 2020 e 2024</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Explore por Região 🗺️")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    
    # Seleção de Região
    regiao_selecionada = st.sidebar.selectbox("Escolha a Região para Análise:", regioes)

    st.subheader(f"Comparativo Climático da Região {regiao_selecionada}: 2020 vs. 2024")
    st.markdown("""
    Esta seção é sua janela para entender a **dinâmica climática** da região selecionada!
    Aqui, você visualiza lado a lado os padrões mensais de **Temperatura Média** e **Precipitação Total** em **2020** e **2024**.
    Observe as diferenças, os picos e os vales: eles contam a história das condições climáticas e podem revelar a influência de eventos anuais ou a variabilidade natural do clima local.
    """)

    # Filtrar dados para a região selecionada e os anos 2020 e 2024
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]
    
    # Assegura que há dados para 2020 e 2024 antes de tentar agrupar
    df_2020 = df_regiao[df_regiao['Ano'] == 2020].groupby('Mês').agg({
        'Temp_Media': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
    }).reindex(range(1, 13))

    df_2024 = df_regiao[df_regiao['Ano'] == 2024].groupby('Mês').agg({
        'Temp_Media': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
    }).reindex(range(1, 13))
    
    if df_2020.dropna().empty or df_2024.dropna().empty:
        st.warning(f"Ops! Parece que não temos dados completos para 2020 ou 2024 na Região **{regiao_selecionada}**. 😕 A comparação completa pode não ser possível. Verifique seus dados ou selecione outra região.")
        st.stop()

    col1, col2 = st.columns(2)

    # Mapeamento de números de mês para nomes
    nomes_meses = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    with col1:
        # --- GRÁFICO DE TEMPERATURA MÉDIA ---
        fig_temp, ax_temp = plt.subplots(figsize=(10, 6))
        
        ax_temp.plot(df_2020.index, df_2020['Temp_Media'], marker='o', linestyle='-', color='#8B008B', label='Temperatura Média 2020', linewidth=2) # Roxo escuro
        ax_temp.plot(df_2024.index, df_2024['Temp_Media'], marker='o', linestyle='--', color='#FF8C00', label='Temperatura Média 2024', linewidth=2) # Laranja vibrante
        
        ax_temp.set_title(f'Temperatura Média Mensal - {regiao_selecionada}', fontsize=18, fontweight='bold', color='#2F4F4F')
        ax_temp.set_xlabel('Mês', fontsize=14)
        ax_temp.set_ylabel('Temperatura Média (°C)', fontsize=14)
        ax_temp.set_xticks(range(1, 13))
        ax_temp.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)])
        ax_temp.grid(True, linestyle=':', alpha=0.7)
        ax_temp.legend(fontsize=12)
        plt.tight_layout()
        st.pyplot(fig_temp)

    with col2:
        # --- GRÁFICO DE PRECIPITAÇÃO TOTAL ---
        fig_prec, ax_prec = plt.subplots(figsize=(10, 6))
        
        ax_prec.bar(df_2020.index - 0.2, df_2020['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], width=0.4, color='#2E8B57', label='Precipitação 2020') # Verde mar
        ax_prec.bar(df_2024.index + 0.2, df_2024['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], width=0.4, color='#4682B4', label='Precipitação 2024') # Azul aço
        
        ax_prec.set_title(f'Precipitação Mensal Total - {regiao_selecionada}', fontsize=18, fontweight='bold', color='#2F4F4F')
        ax_prec.set_xlabel('Mês', fontsize=14)
        ax_prec.set_ylabel('Precipitação Total (mm)', fontsize=14)
        ax_prec.set_xticks(range(1, 13))
        ax_prec.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)])
        ax_prec.grid(axis='y', linestyle=':', alpha=0.7)
        ax_prec.legend(fontsize=12)
        plt.tight_layout()
        st.pyplot(fig_prec)

    st.markdown("---")

    # --- ANÁLISE PROFUNDA E JUSTIFICATIVA ---
    st.header(f"2020 vs. 2024 na Região {regiao_selecionada}: Eventos Climáticos ou Variabilidade Natural? 🤔")
    st.markdown(f"""
    Ao confrontar os padrões climáticos de **2020** e **2024** para a **Região {regiao_selecionada}**, podemos desvendar narrativas cruciais sobre a natureza do clima local. As diferenças observadas nesses gráficos podem ser mais do que simples flutuações anuais; elas podem sinalizar a influência de **eventos climáticos específicos** ou, alternativamente, a manifestação de uma **alta variabilidade intrínseca** à região.
    """)

    st.markdown("### Análise da Temperatura Média: O Que as Curvas Revelam? 📈")
    st.markdown("""
    Observe as linhas de temperatura. Se a linha de **2024** se mantém consistentemente acima (ou abaixo) da de **2020** por vários meses, especialmente em estações-chave, isso pode indicar:
    * **Tendência de Aquecimento/Resfriamento Anual:** Um ano **visivelmente mais quente (ou frio)** que o outro sugere uma possível aceleração de tendências de longo prazo, ou a influência de fenômenos de grande escala (como El Niño/La Niña intensos).
    * **Eventos Extremos de Calor/Frio:** Picos ou vales acentuados em meses específicos de um ano, sem correspondência no outro, podem indicar **ondas de calor ou frio** pontuais, que são eventos climáticos de alto impacto para a saúde e a economia.
    """)

    st.markdown("### Análise da Precipitação Total: A Dança das Chuvas 🌧️")
    st.markdown("""
    A comparação das barras de precipitação é igualmente reveladora. Diferenças significativas nos volumes mensais entre os dois anos podem apontar para:
    * **Secas ou Chuvas Intensas:** Um ano com volumes de precipitação drasticamente menores ou maiores que o outro (especialmente durante a estação chuvosa) sugere a ocorrência de **secas prolongadas ou períodos de chuvas torrenciais**. Estes são eventos climáticos extremos com sérias consequências para recursos hídricos e agricultura.
    * **Mudança na Sazonalidade:** Se os picos de chuva ocorreram em meses diferentes, ou se a distribuição das chuvas mudou (ex: um ano com chuva mais concentrada, outro mais dispersa), isso aponta para uma **alteração nos padrões sazonais**, uma manifestação de alta variabilidade que exige adaptabilidade.
    """)

    st.markdown("### Conclusão: Eventos Climáticos ou Alta Variabilidade? A Resposta Está nos Dados! 💡")
    st.markdown("""
    * **Eventos Climáticos Dominantes:** Se você observar diferenças **abruptas e marcantes** em um ou mais meses, ou um padrão de temperaturas ou precipitações consistentemente mais altas/baixas em um ano versus outro, isso **fortemente sugere a influência de um evento climático específico** naquele período. Estes podem ser El Niño/La Niña, bloqueios atmosféricos, ou a passagem de ciclones que impactam diretamente a região.
    * **Alta Variabilidade Intrínseca:** Por outro lado, se as diferenças são **menos consistentes**, com um ano sendo mais quente em alguns meses e mais frio em outros, ou com variações de precipitação que não formam um padrão claro de seca/enchente generalizada, isso pode indicar uma **alta variabilidade climática intrínseca à região**. Esta variabilidade exige adaptabilidade contínua por parte dos setores econômicos e da população, pois as condições podem mudar rapidamente de um ano para o outro.

    Ao analisar cuidadosamente os gráficos acima, você pode inferir se a Região **{regiao_selecionada}** vivenciou anomalias climáticas pontuais em 2020 ou 2024, ou se a sua variabilidade natural foi particularmente acentuada nesses anos. Qual narrativa climática sua região conta?
    """)

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"Erro: O arquivo **'{caminho_arquivo_unificado}'** não foi encontrado. Por favor, verifique o caminho e a localização do arquivo em seu projeto. 📁")
except KeyError as e:
    st.error(f"Erro de Coluna: A coluna **'{e}'** não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém os dados necessários para a análise (Temperatura Média, Precipitação Total). 🧐")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado durante a execução do aplicativo: **{e}** 🐛. Por favor, tente novamente ou entre em contato com o suporte.")
