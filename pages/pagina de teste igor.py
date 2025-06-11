import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Contraste Climático 2020-2024 🌎")

st.title("🌡️ Contrastando o Clima: Padrões de Temperatura e Precipitação no Brasil (2020 vs. 2024) ☔")
st.markdown("""
Bem-vindo(a) à nossa ferramenta interativa para **decifrar as nuances climáticas** entre os anos de **2020 e 2024** no Brasil!
Use a barra lateral para selecionar uma região e explore como a **temperatura média** e a **precipitação total** se comportaram nesses dois períodos.
Prepare-se para descobrir se as diferenças observadas são variabilidade natural ou indícios de eventos climáticos marcantes.
""")

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS (com caching) ---
@st.cache_data
def carregar_dados(caminho):
    """
    Carrega e processa o arquivo de dados climáticos.
    Realiza o cálculo da temperatura média e garante que as colunas essenciais são numéricas.
    """
    df = pd.read_csv(caminho)
    
    # Calcula a Temp_Media se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] + 
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    else:
        # Se as colunas de max/min não existirem, 'Temp_Media' precisa estar no CSV
        if 'Temp_Media' not in df.columns:
            st.error("❌ **Erro Crítico:** As colunas de temperatura máxima e mínima não foram encontradas, e a coluna 'Temp_Media' também está ausente. Não é possível prosseguir. Por favor, verifique seu arquivo CSV! 🚨")
            st.stop()

    # Converte colunas para numérico, tratando erros
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    
    # Garante que as colunas necessárias existem após o cálculo/verificação
    required_cols = ['Temp_Media', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ **Erro Crítico:** A coluna essencial '{col}' não foi encontrada no arquivo CSV. Verifique a integridade dos seus dados. 🛑")
            st.stop()

    df = df.dropna(subset=['Mês', 'Ano', 'Regiao'] + required_cols)
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS INICIAIS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)
    
    # Verifica se a coluna de temperatura média pôde ser criada ou se já existia (redundância para clareza)
    if 'Temp_Media' not in df_unificado.columns:
        st.error("⚠️ **Problema na Coluna de Temperatura:** A coluna 'Temp_Media' não foi encontrada e não pôde ser calculada. Certifique-se de que as colunas 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' e 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' (ou 'Temp_Media') estão presentes no seu arquivo CSV. 🚧")
        st.stop()

    # --- INTERFACE DO USUÁRIO NA BARRA LATERAL ---
    st.sidebar.header("⚙️ Configure sua Comparação:")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    
    # Seleção de Região
    regiao_selecionada = st.sidebar.selectbox("📍 Selecione a Região para Analisar:", regioes)

    st.subheader(f"Comparativo Climático entre 2020 e 2024 na Região: **{regiao_selecionada}**")
    st.markdown("""
    Esta seção é o coração da nossa análise! Aqui, você verá lado a lado os padrões de **Temperatura Média** e **Precipitação Total**
    registrados em **2020** e **2024** para a região escolhida.
    Observe com atenção: as diferenças podem revelar a **impressão digital de eventos climáticos significativos** ou a **dinâmica da variabilidade natural** da região.
    """)

    # Filtrar dados para a região selecionada e os anos 2020 e 2024
    df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]
    
    df_2020 = df_regiao[df_regiao['Ano'] == 2020].groupby('Mês').agg({
        'Temp_Media': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
    }).reindex(range(1, 13)).dropna()

    df_2024 = df_regiao[df_regiao['Ano'] == 2024].groupby('Mês').agg({
        'Temp_Media': 'mean',
        'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
    }).reindex(range(1, 13)).dropna()
    
    if df_2020.empty or df_2024.empty:
        st.warning(f"❗ **Atenção:** Dados incompletos para um ou ambos os anos (2020/2024) na Região **{regiao_selecionada}**. Não é possível realizar uma comparação completa. 😔")
        st.info("Isso pode acontecer se não houver registros para todos os meses nesses anos. Tente selecionar outra região, ou verifique a base de dados. ")
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
        
        ax_temp.plot(df_2020.index, df_2020['Temp_Media'], marker='o', linestyle='-', color='#E67E22', label='Temperatura Média 2020', linewidth=2.5) # Laranja vibrante
        ax_temp.plot(df_2024.index, df_2024['Temp_Media'], marker='x', linestyle='--', color='#3498DB', label='Temperatura Média 2024', linewidth=2.5) # Azul céu
        
        ax_temp.set_title(f'Termômetro Mensal: {regiao_selecionada} 🌡️', fontsize=18, fontweight='bold', color='#2C3E50')
        ax_temp.set_xlabel('Mês', fontsize=14, color='#34495E')
        ax_temp.set_ylabel('Temperatura Média (°C)', fontsize=14, color='#34495E')
        ax_temp.set_xticks(range(1, 13))
        ax_temp.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)], fontsize=10)
        ax_temp.tick_params(axis='y', labelsize=10)
        ax_temp.grid(True, linestyle=':', alpha=0.6, color='#BDC3C7')
        ax_temp.legend(fontsize=11, frameon=True, shadow=True, fancybox=True)
        ax_temp.set_facecolor('#F8F9FA') # Levemente cinza para o fundo do gráfico
        plt.tight_layout()
        st.pyplot(fig_temp)

    with col2:
        # --- GRÁFICO DE PRECIPITAÇÃO TOTAL ---
        fig_prec, ax_prec = plt.subplots(figsize=(10, 6))
        
        ax_prec.bar(df_2020.index - 0.2, df_2020['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], width=0.4, color='#27AE60', label='Precipitação 2020', alpha=0.9) # Verde esmeralda
        ax_prec.bar(df_2024.index + 0.2, df_2024['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'], width=0.4, color='#8E44AD', label='Precipitação 2024', alpha=0.9) # Roxo
        
        ax_prec.set_title(f'Volume de Chuvas Mensal: {regiao_selecionada} ☔', fontsize=18, fontweight='bold', color='#2C3E50')
        ax_prec.set_xlabel('Mês', fontsize=14, color='#34495E')
        ax_prec.set_ylabel('Precipitação Total (mm)', fontsize=14, color='#34495E')
        ax_prec.set_xticks(range(1, 13))
        ax_prec.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)], fontsize=10)
        ax_prec.tick_params(axis='y', labelsize=10)
        ax_prec.grid(axis='y', linestyle=':', alpha=0.6, color='#BDC3C7')
        ax_prec.legend(fontsize=11, frameon=True, shadow=True, fancybox=True)
        ax_prec.set_facecolor('#F8F9FA') # Levemente cinza para o fundo do gráfico
        plt.tight_layout()
        st.pyplot(fig_prec)

    st.markdown("---")

    # --- ANÁLISE PROFUNDA E JUSTIFICATIVA ---
    st.header(f"🕵️‍♀️ 2020 vs. 2024 na Região {regiao_selecionada}: Eventos Climáticos ou Variabilidade Natural? 🤷")
    st.markdown(f"""
    Ao confrontar os padrões climáticos de **2020** e **2024** para a **Região {regiao_selecionada}**, podemos extrair **insights cruciais** sobre a dinâmica do clima local. As diferenças que você observou nos gráficos acima podem ser mais do que simples flutuações anuais; elas podem sinalizar a **influência de eventos climáticos específicos** ou, alternativamente, a **manifestação da alta variabilidade intrínseca** da região.

    ### Análise da Temperatura Média: O que os Termômetros nos Dizem? 📈
    Observe as linhas de temperatura com atenção. Se a linha de **2024** se mantém consistentemente **acima (ou abaixo) da de 2020** por vários meses, especialmente em estações-chave, isso pode indicar:
    * **Tendência Anual de Aquecimento/Resfriamento:** Um ano **visivelmente mais quente (ou frio)** que o outro sugere uma possível aceleração de tendências de longo prazo ou a influência de fenômenos de grande escala, como um **El Niño** (aquecimento) ou **La Niña** (resfriamento) intensos.
    * **Eventos Extremos de Calor/Frio:** Picos ou vales acentuados em meses específicos de um ano, sem correspondência no outro, podem indicar **ondas de calor ou frio** pontuais, que são eventos climáticos de alto impacto e podem causar estresse em ecossistemas e populações.

    ### Análise da Precipitação Total: A História das Chuvas 🌧️
    A comparação das barras de precipitação é igualmente reveladora. Diferenças significativas nos volumes mensais entre os dois anos podem apontar para:
    * **Secas ou Chuvas Intensas:** Um ano com volumes de precipitação drasticamente menores ou maiores que o outro (especialmente durante a estação chuvosa) sugere a ocorrência de **secas prolongadas** ou **períodos de chuvas torrenciais**. Estes são eventos climáticos extremos com sérias consequências para a agricultura, recursos hídricos e risco de desastres naturais.
    * **Mudança na Sazonalidade:** Se os picos de chuva ocorreram em meses diferentes, ou se a distribuição das chuvas mudou (ex: um ano com chuva mais concentrada, outro mais dispersa), isso aponta para uma **alteração nos padrões sazonais**, uma manifestação de alta variabilidade climática.

    ### Conclusão: Eventos Climáticos Pontuais ou Alta Variabilidade Climática? 🤔
    * **Eventos Climáticos Dominantes:** Se você observar diferenças **abruptas e marcantes** em um ou mais meses, ou um padrão de temperaturas ou precipitações consistentemente mais altas/baixas em um ano versus outro, isso **fortemente sugere a influência de um evento climático específico** naquele período. Estes podem ser El Niño/La Niña, bloqueios atmosféricos, ou a passagem de ciclones que impactam diretamente a região.
    * **Alta Variabilidade Climática:** Por outro lado, se as diferenças são **menos consistentes**, com um ano sendo mais quente em alguns meses e mais frio em outros, ou com variações de precipitação que não formam um padrão claro de seca/enchente generalizada, isso pode indicar uma **alta variabilidade climática intrínseca à região**. Esta variabilidade exige uma **adaptação contínua** por parte dos setores econômicos (como a agricultura) e da população em geral.

    Ao analisar cuidadosamente os gráficos acima, você pode inferir se a **Região {regiao_selecionada}** vivenciou anomalias climáticas pontuais em 2020 ou 2024, ou se a sua variabilidade natural foi particularmente acentuada nesses anos.
    """)

# --- TRATAMENTO GERAL DE ERROS ---
except FileNotFoundError:
    st.error(f"❌ **Erro:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e a localização do arquivo CSV. 🧐")
except KeyError as e:
    st.error(f"⚠️ **Erro de Coluna:** A coluna '{e}' não foi encontrada no seu arquivo CSV. Verifique se o seu arquivo contém todos os cabeçalhos de dados necessários para a análise. 😬")
except Exception as e:
    st.error(f"💥 **Ocorreu um erro inesperado!** Parece que algo deu errado durante o processamento. Por favor, tente novamente. Se o problema persistir, entre em contato com o suporte ou verifique os dados. Detalhes técnicos: `{e}`")

st.markdown("---")
st.markdown("✨ Análise climática facilitada para você! Quais outras comparações ou períodos você gostaria de investigar? ✨")
