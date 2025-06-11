import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(layout="wide", page_title="Análise de Radiação Global no Brasil ☀️")

# CSS para estilização aprimorada do título
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fa; /* Fundo suave para o aplicativo */
}
.main-title {
    font-size: 3.5em;
    font-weight: 700;
    color: #2E8B57; /* Um verde mais escuro e atraente */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle {
    font-size: 1.8em;
    color: #3CB371; /* Um verde um pouco mais claro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section {
    background-color: #e6f7ee; /* Fundo levemente verde para a seção de cabeçalho */
    padding: 1.5em;
    border-radius: 10px;
    margin-bottom: 2em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
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
    # Converte colunas para numérico, tratando erros
    for col in ['Ano', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['Ano', 'Mês', 'RADIACAO GLOBAL (Kj/m²)'])
    return df

try:
    # Carregar os dados
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # Verificar se as colunas necessárias existem
    colunas_necessarias_existentes = ['Ano', 'Regiao', 'Mês', 'RADIACAO GLOBAL (Kj/m²)']
    for coluna in colunas_necessarias_existentes:
        if coluna not in df_unificado.columns:
            raise KeyError(f"A coluna '{coluna}' não foi encontrada no arquivo CSV. Verifique o seu arquivo.")

    # --- TÍTULO PRINCIPAL E SUBTÍTULO COM EMOJIS ---
    st.markdown('<div class="header-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Análise Personalizada de Radiação Global ☀️📊</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explorando Padrões Climáticos no Brasil (2020-2025) 🇧🇷</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- EXPLICAÇÃO INICIAL DO APP ---
    st.markdown("---")
    st.header("Entendendo a Análise de Radiação Global")
    st.markdown("""
        Este aplicativo Streamlit permite uma exploração detalhada da **Radiação Global média**
        para as regiões do Brasil entre 2020 e 2025. Ao selecionar um ano, mês e região específicos,
        você pode entender as condições de radiação solar para aquele período e local, além de
        compará-las com médias mais amplas.
        """)

    # --- WIDGETS DE SELEÇÃO NA SIDEBAR ---
    st.sidebar.header("Selecione os Filtros")
    
    # Selecionar ano
    anos_disponiveis = sorted(df_unificado['Ano'].unique())
    ano_selecionado = st.sidebar.selectbox(
        "Ano:",
        options=anos_disponiveis,
        index=len(anos_disponiveis)-1 if 2023 not in anos_disponiveis else anos_disponiveis.index(2023)
    )
    
    # Dicionário de meses
    meses_nome = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    # Filtrar meses disponíveis para o ano selecionado
    meses_disponiveis_ano = sorted(df_unificado[df_unificado['Ano'] == ano_selecionado]['Mês'].unique())
    meses_nome_disponiveis = [meses_nome[mes] for mes in meses_disponiveis_ano]
    
    # Selecionar mês
    mes_selecionado_nome = st.sidebar.selectbox(
        "Mês:",
        options=meses_nome_disponiveis,
        index=0  # Sempre começa com o primeiro mês disponível
    )
    
    # Obter o número do mês selecionado
    mes_selecionado = [num for num, nome in meses_nome.items() if nome == mes_selecionado_nome][0]
    
    # Selecionar região
    regioes_disponiveis = sorted(df_unificado['Regiao'].unique())
    regiao_selecionada = st.sidebar.selectbox(
        "Região:",
        options=regioes_disponiveis,
        index=0  # Sempre começa com a primeira região disponível
    )

    st.markdown("---")
    # --- ANÁLISE PARA O ANO, MÊS E REGIÃO SELECIONADOS ---
    st.header(f"Análise para {mes_selecionado_nome} de {ano_selecionado} - Região {regiao_selecionada}")
    st.subheader("Métricas Principais")
    st.markdown("""
        Após aplicar os filtros, esta seção exibe uma análise focada na Radiação Global
        para o período e região escolhidos, através de métricas rápidas.
        """)

    # Filtrar dados para a seleção
    df_filtrado = df_unificado[
        (df_unificado['Ano'] == ano_selecionado) &
        (df_unificado['Mês'] == mes_selecionado) &
        (df_unificado['Regiao'] == regiao_selecionada)
    ]

    if df_filtrado.empty:
        st.warning(f"Não foram encontrados dados para a região {regiao_selecionada} em {mes_selecionado_nome}/{ano_selecionado}.")
    else:
        # Calcular média para a região selecionada
        media_regiao = df_filtrado['RADIACAO GLOBAL (Kj/m²)'].mean()
        
        # Comparar com a média geral do mês
        media_geral_mes = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Mês'] == mes_selecionado)
        ]['RADIACAO GLOBAL (Kj/m²)'].mean()
        
        # Comparar com a média anual da região
        media_anual_regiao = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Regiao'] == regiao_selecionada)
        ]['RADIACAO GLOBAL (Kj/m²)'].mean()

        # Exibir métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Radiação em {mes_selecionado_nome}",
                value=f"{media_regiao:.2f} Kj/m²",
                delta=f"{(media_regiao - media_geral_mes):.2f} Kj/m² vs média geral do mês"
            )
        with col2:
            st.metric(
                label="Média Geral do Mês (todas regiões)",
                value=f"{media_geral_mes:.2f} Kj/m²"
            )
        with col3:
            st.metric(
                label="Média Anual da Região",
                value=f"{media_anual_regiao:.2f} Kj/m²",
                delta=f"{(media_regiao - media_anual_regiao):.2f} Kj/m² vs média anual da região"
            )

        st.markdown("""
            Essas métricas permitem identificar rapidamente se a radiação no período escolhido
            foi acima ou abaixo da média regional e nacional.
            """)

        # --- GRÁFICO DE COMPARAÇÃO REGIONAL ---
        st.markdown("---")
        st.subheader(f"Comparação Regional para {mes_selecionado_nome}/{ano_selecionado}")
        st.markdown("""
            Este gráfico de barras compara a Radiação Global média entre todas as regiões do Brasil
            para o mês e ano selecionados.
            **Propósito:** Este gráfico permite identificar quais regiões tiveram os maiores e menores
            níveis de radiação para aquele período específico. A região que você selecionou nos filtros
            da barra lateral será destacada para fácil visualização.
            **Interpretação:** Regiões com barras mais altas indicam maior incidência de radiação solar,
            o que pode ser relevante para setores como energia solar fotovoltaica e agricultura.
            """)

        # Dados para comparação
        df_comparacao = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Mês'] == mes_selecionado)
        ].groupby('Regiao')['RADIACAO GLOBAL (Kj/m²)'].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Cores - destacar a região selecionada
        cores = ['lightgray' if regiao != regiao_selecionada else 'coral'
                 for regiao in df_comparacao.index]
        
        bars = ax.bar(df_comparacao.index, df_comparacao.values, color=cores)
        
        ax.set_xlabel('Região')
        ax.set_ylabel('Radiação Global Média (Kj/m²)')
        ax.set_title(f'Comparação Regional - {mes_selecionado_nome}/{ano_selecionado}')
        ax.tick_params(axis='x', rotation=45) # Rotaciona os rótulos do eixo X para melhor visualização
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Adicionar valores nas barras
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05*yval,
                            f'{yval:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        st.pyplot(fig)

        # --- EVOLUÇÃO MENSAL DA REGIÃO SELECIONADA ---
        st.markdown("---")
        st.subheader(f"Evolução Mensal em {ano_selecionado} - Região {regiao_selecionada}")
        st.markdown("""
            Este gráfico de linha ilustra a variação da Radiação Global média mês a mês
            para a região e o ano selecionados.
            **Propósito:** Ajuda a visualizar a sazonalidade da radiação solar na região,
            observando os picos e vales ao longo do ano.
            **Destaque:** O mês que você selecionou no filtro da barra lateral será marcado
            no gráfico com uma linha tracejada, facilitando a localização do seu ponto de
            interesse dentro do padrão anual.
            **Interpretação:** Padrões consistentes de alta ou baixa radiação em certos meses
            podem influenciar o planejamento de atividades que dependem da luz solar, como o
            agronegócio ou a otimização de sistemas solares.
            """)

        df_evolucao = df_unificado[
            (df_unificado['Ano'] == ano_selecionado) &
            (df_unificado['Regiao'] == regiao_selecionada)
        ].groupby('Mês')['RADIACAO GLOBAL (Kj/m²)'].mean()

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(df_evolucao.index, df_evolucao.values, marker='o', color='coral')
        
        # Destacar o mês selecionado
        if mes_selecionado in df_evolucao.index:
            ax2.axvline(x=mes_selecionado, color='gray', linestyle='--', alpha=0.5)
            # Ajuste da posição do texto para não sair do gráfico
            y_text_pos = ax2.get_ylim()[1] * 0.9 if ax2.get_ylim()[1] * 0.9 > ax2.get_ylim()[0] else ax2.get_ylim()[1] * 0.7
            ax2.text(mes_selecionado, y_text_pos,
                            f'Mês selecionado\n{mes_selecionado_nome}',
                            ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Radiação Global Média (Kj/m²)')
        ax2.set_title(f'Evolução Mensal - Região {regiao_selecionada} - {ano_selecionado}')
        ax2.set_xticks(range(1, 13))
        ax2.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig2)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Verifique o caminho e a estrutura de pastas.")
except KeyError as e:
    st.error(f"Erro: A coluna {e} não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto no código e no arquivo.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {str(e)}")
