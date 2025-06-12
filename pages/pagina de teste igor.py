import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap # Not directly used in the final version but good to keep if styling changes

# --- Configurações Iniciais e Estilo da Página ---
st.set_page_config(
    layout="wide",
    page_title="Análise Climática Brasil: 2020 vs. 2024",
    page_icon="🌍"
)

# Título Principal da Aplicação
st.title("🌍 Contrastando o Clima: Padrões de Temperatura e Precipitação entre 2020 e 2024 no Brasil")

st.markdown("""
Uma imersão visual nos dados climáticos brasileiros, revelando as dinâmicas de temperatura e precipitação
entre os anos de 2020 e 2024. Explore como as condições climáticas variaram em diferentes regiões do país.
""")

# Caminho relativo ao arquivo CSV
# Certifique-se de que o arquivo 'medias_mensais_geo_2020_2025.csv'
# esteja localizado dentro de uma pasta 'medias' no mesmo diretório da sua aplicação Streamlit.
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- Função para Carregar e Preparar os Dados ---
@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    """
    Carrega e processa o arquivo de dados climáticos CSV.
    Realiza o cálculo da temperatura média se as colunas de máxima e mínima estiverem presentes,
    e garante que as colunas essenciais estejam no DataFrame.

    Args:
        caminho (str): O caminho para o arquivo CSV de dados climáticos.

    Returns:
        pd.DataFrame: O DataFrame processado com os dados climáticos.

    Raises:
        st.error: Interrompe a execução do Streamlit se colunas críticas estiverem faltando.
    """
    try:
        df = pd.read_csv(caminho)
    except FileNotFoundError:
        st.error(f"Erro Crítico: O arquivo '{caminho}' não foi encontrado. Verifique o caminho e a localização do arquivo.")
        st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        st.stop()

    # Calcula a Temp_Media se as colunas de max/min existirem
    if 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)' in df.columns and \
       'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)' in df.columns:
        df['Temp_Media'] = (df['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'] +
                            df['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)']) / 2
    elif 'Temp_Media' not in df.columns:
        # Se Temp_Media não existe e não pôde ser calculada, levanta um erro crítico.
        st.error("Erro Crítico: A coluna 'Temp_Media' não existe e não pôde ser calculada a partir das colunas de máxima e mínima. Verifique o seu arquivo CSV.")
        st.stop()

    # Converte colunas essenciais para numérico, tratando erros com 'coerce'
    df['Mês'] = pd.to_numeric(df['Mês'], errors='coerce')
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')

    # Garante que as colunas necessárias para a análise existem
    required_cols = ['Temp_Media', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)', 'Regiao', 'Mês', 'Ano']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Erro Crítico: A coluna '{col}' não foi encontrada no arquivo CSV. Verifique seu arquivo.")
            st.stop()

    # Remove linhas com valores nulos nas colunas críticas após a conversão
    df = df.dropna(subset=required_cols)
    return df

# --- Carregamento dos Dados e Tratamento de Erros Iniciais ---
df_unificado = carregar_dados(caminho_arquivo_unificado)

# --- Interface do Usuário na Barra Lateral ---
st.sidebar.header("⚙️ Opções de Análise")

# Obter lista única de regiões para o selectbox, ordenadas alfabeticamente
regioes = sorted(df_unificado['Regiao'].unique())

# Seleção de Região
regiao_selecionada = st.sidebar.selectbox(
    "Selecione a Região para Comparação:",
    regioes,
    help="Escolha uma região para visualizar o comparativo climático entre 2020 e 2024."
)

st.sidebar.markdown("---")
st.sidebar.info("✨ Dados fornecidos para a comparação de padrões climáticos anuais no Brasil.")

# --- Seção Principal da Aplicação ---
st.subheader(f"📊 Comparativo Climático Detalhado: 2020 vs. 2024 na Região {regiao_selecionada}")
st.markdown("""
Esta seção apresenta uma análise lado a lado dos padrões de **Temperatura Média** e **Precipitação Total**
para a região selecionada, contrastando os dados de **2020** com os de **2024**. As diferenças observadas
podem indicar tendências climáticas, a influência de eventos anuais específicos ou a variabilidade natural do clima local.
""")

# Filtrar dados para a região selecionada e os anos 2020 e 2024
df_regiao = df_unificado[df_unificado['Regiao'] == regiao_selecionada]

# Agrupar e reindexar dados por mês para 2020 e 2024
# Garante que todos os 12 meses estão presentes, mesmo que com NaN se não houver dados.
df_2020 = df_regiao[df_regiao['Ano'] == 2020].groupby('Mês').agg({
    'Temp_Media': 'mean',
    'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
}).reindex(range(1, 13))

df_2024 = df_regiao[df_regiao['Ano'] == 2024].groupby('Mês').agg({
    'Temp_Media': 'mean',
    'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)': 'sum'
}).reindex(range(1, 13))

# Remover meses onde não há dados para ambos os anos na comparação de gráficos
df_2020_comp = df_2020.dropna()
df_2024_comp = df_2024.dropna()

if df_2020_comp.empty or df_2024_comp.empty:
    st.warning(f"Dados incompletos para 2020 ou 2024 na Região {regiao_selecionada}. Não é possível realizar a comparação completa.")
    # Não st.stop() aqui para permitir que a explicação continue, mas o gráfico não será gerado
else:
    # Mapeamento de números de mês para nomes abreviados
    nomes_meses = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    # Layout de colunas para os gráficos
    col1, col2 = st.columns(2)

    with col1:
        # --- GRÁFICO DE TEMPERATURA MÉDIA ---
        fig_temp, ax_temp = plt.subplots(figsize=(10, 6))

        ax_temp.plot(df_2020_comp.index, df_2020_comp['Temp_Media'], marker='o', linestyle='-',
                     color='purple', label='Temperatura Média 2020', linewidth=2, markersize=7)
        ax_temp.plot(df_2024_comp.index, df_2024_comp['Temp_Media'], marker='o', linestyle='--',
                     color='orange', label='Temperatura Média 2024', linewidth=2, markersize=7)

        ax_temp.set_title(f'Variação da Temperatura Média Mensal\nRegião: {regiao_selecionada}', fontsize=16, fontweight='bold')
        ax_temp.set_xlabel('Mês', fontsize=12)
        ax_temp.set_ylabel('Temperatura Média (°C)', fontsize=12)
        ax_temp.set_xticks(range(1, 13))
        ax_temp.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)])
        ax_temp.grid(True, linestyle=':', alpha=0.7)
        ax_temp.legend(fontsize=10, loc='best')
        plt.tight_layout()
        st.pyplot(fig_temp)

    with col2:
        # --- GRÁFICO DE PRECIPITAÇÃO TOTAL ---
        fig_prec, ax_prec = plt.subplots(figsize=(10, 6))

        # Ajusta a posição das barras para ficarem lado a lado
        bar_width = 0.4
        ax_prec.bar(df_2020_comp.index - bar_width/2, df_2020_comp['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'],
                    width=bar_width, color='darkgreen', label='Precipitação 2020', alpha=0.8)
        ax_prec.bar(df_2024_comp.index + bar_width/2, df_2024_comp['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'],
                    width=bar_width, color='skyblue', label='Precipitação 2024', alpha=0.8)

        ax_prec.set_title(f'Volume Total de Precipitação Mensal\nRegião: {regiao_selecionada}', fontsize=16, fontweight='bold')
        ax_prec.set_xlabel('Mês', fontsize=12)
        ax_prec.set_ylabel('Precipitação Total (mm)', fontsize=12)
        ax_prec.set_xticks(range(1, 13))
        ax_prec.set_xticklabels([nomes_meses.get(m, str(m)) for m in range(1, 13)])
        ax_prec.grid(axis='y', linestyle=':', alpha=0.7)
        ax_prec.legend(fontsize=10, loc='best')
        plt.tight_layout()
        st.pyplot(fig_prec)

st.markdown("---")

# --- ANÁLISE PROFUNDA E JUSTIFICATIVA ---
st.header(f"🔍 2020 vs. 2024 na Região {regiao_selecionada}: Eventos Climáticos ou Variabilidade Natural?")
st.markdown(f"""
Ao confrontar os padrões climáticos de **2020** e **2024** para a **Região {regiao_selecionada}**,
podemos extrair insights cruciais sobre a natureza do clima local. As diferenças visíveis nos gráficos
acima podem ser mais do que meras flutuações anuais; elas podem sinalizar a influência de eventos climáticos
específicos ou, alternativamente, a manifestação de uma alta variabilidade intrínseca à região.

---

### 🌡️ Análise da Temperatura Média:
Observe as linhas que representam a temperatura média mensal.

* **Tendência Anual:** Se a linha de **2024** se mantém consistentemente acima (ou abaixo) da de **2020** por
    vários meses, especialmente em estações-chave, isso pode indicar uma **tendência de aquecimento ou
    resfriamento anual** mais acentuada. Isso pode ser um reflexo de tendências climáticas de longo prazo
    ou a influência de fenômenos de grande escala, como fases intensas do El Niño/La Niña.
* **Eventos Extremos de Calor/Frio:** Picos ou vales acentuados em meses específicos de um ano, sem uma
    correspondência similar no outro, podem indicar a ocorrência de **ondas de calor ou frio pontuais**.
    Estes são eventos climáticos de alto impacto que merecem atenção especial.

---

### ☔ Análise da Precipitação Total:
A comparação das barras de precipitação é igualmente reveladora para entender os regimes hídricos.

* **Secas ou Chuvas Intensas:** Um ano com volumes de precipitação drasticamente menores ou maiores que
    o outro (especialmente durante a estação chuvosa característica da região) sugere a ocorrência de
    **secas prolongadas ou períodos de chuvas torrenciais**. Tais eventos são extremos e podem ter
    consequências severas para a agricultura, recursos hídricos e cidades.
* **Mudança na Sazonalidade:** Se os picos de chuva ocorreram em meses diferentes, ou se a distribuição
    das chuvas mudou significativamente (por exemplo, um ano com chuva mais concentrada em poucos meses,
    outro mais dispersa ao longo do ano), isso aponta para uma **alteração nos padrões sazonais**.
    Esta é uma indicação clara de alta variabilidade climática.

---

### 🧐 Conclusão: Eventos Climáticos ou Alta Variabilidade?
* **Impacto de Eventos Climáticos:** Se você observar diferenças **abruptas e marcantes** em um ou mais meses,
    ou um padrão de temperaturas ou precipitações consistentemente mais altas/baixas em um ano em
    comparação ao outro, isso **sugere fortemente a influência de um evento climático específico** naquele período.
    Estes podem incluir fenômenos como El Niño/La Niña, bloqueios atmosféricos, ou a passagem de sistemas ciclônicos.
* **Alta Variabilidade Natural:** Por outro lado, se as diferenças são **menos consistentes**, com um ano
    sendo mais quente em alguns meses e mais frio em outros, ou com variações de precipitação que não
    formam um padrão claro de seca/enchente generalizada, isso pode indicar uma **alta variabilidade
    climática intrínseca à região**. Esta variabilidade exige adaptabilidade contínua por parte de
    diversos setores, como o agrícola e de infraestrutura.

Ao analisar cuidadosamente os gráficos e as informações acima, você pode inferir se a **Região {regiao_selecionada}**
vivenciou anomalias climáticas pontuais em 2020 ou 2024, ou se a sua variabilidade natural foi particularmente acentuada nesses anos.
""")

# --- Rodapé ou Informações Adicionais (Opcional) ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: small; color: gray;'>
    Dados baseados em informações meteorológicas históricas.
    Desenvolvido para análise comparativa de padrões climáticos.
</div>
""", unsafe_allow_html=True)

# Lembre-se: Para rodar este código, você precisa ter o Streamlit instalado
# (`pip install streamlit pandas matplotlib`) e salvar o código como um arquivo `.py`
# (ex: `app_clima.py`). Coloque o arquivo `medias_mensais_geo_2020_2025.csv`
# dentro de uma pasta `medias` no mesmo diretório da aplicação.
# Em seguida, execute no terminal: `streamlit run app_clima.py`
