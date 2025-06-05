import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Médias Mensais Regionais (2020-2025) - Visualização por Região e Variável")

try:
    # Ler o arquivo unificado
    df_unificado = pd.read_csv(caminho_arquivo_unificado)

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
    fig, ax = plt.subplots(figsize=(10, 6)) # Aumentei um pouco o tamanho do gráfico
    
    # Plotagem dos dados
    for ano in anos:
        df_ano_regiao = df_regiao[df_regiao['Ano'] == ano].groupby('Mês')[coluna_var].mean().reindex(meses)
        if not df_ano_regiao.empty:
            ax.plot(meses, df_ano_regiao.values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
            
    ax.set_title(f'Média Mensal de {nome_var} - {regiao_selecionada} (2020-2025)')
    ax.set_xlabel('Mês')
    ax.set_ylabel(nome_var)
    ax.set_xticks(meses)
    ax.grid(True)
    ax.legend(title='Ano')
    plt.tight_layout()
    st.pyplot(fig)

    # --- Nova Seção de Análise Sazonal e Atípica ---
    if nome_var == 'Temperatura Média (°C)':
        st.write("---") # Linha divisória para melhor organização
        st.subheader(f"Análise dos Padrões Sazonais de Temperatura na Região {regiao_selecionada}")

        if regiao_selecionada == 'Sudeste':
            st.write("""
            A **Região Sudeste** (SP, RJ, MG, ES) exibe as quatro estações do ano bem definidas em termos de temperatura:

            * **Verão (Dez-Mar):** Período mais **quente e úmido**, com temperaturas médias elevadas. Nos gráficos, são os picos anuais.
            * **Outono (Abr-Jun):** **Transição** para o frio, com temperaturas em declínio gradual.
            * **Inverno (Jul-Set):** Estação mais **fria**, com as menores temperaturas médias do ano. Nos gráficos, são os vales anuais. Pode haver massas de ar polar.
            * **Primavera (Out-Nov):** **Transição** para o calor, com temperaturas em ascensão gradual.

            **Para identificar meses/anos atípicos (2020-2025):**
            Observe as linhas de cada ano no gráfico. Se uma linha estiver **significativamente acima** (mais quente) ou **abaixo** (mais fria) da média dos outros anos para um determinado mês, isso indica um evento atípico. Por exemplo, **Maio de 2025** pode mostrar temperaturas atipicamente baixas devido a fortes frentes frias, enquanto "veranicos" podem causar picos de calor em meses que deveriam ser mais amenos.
            """)
        elif regiao_selecionada == 'Nordeste':
            st.write("""
            A **Região Nordeste** apresenta temperaturas **elevadas e mais estáveis** ao longo do ano, com menor variação sazonal do que o Sudeste. As estações são mais marcadas pelo regime de chuvas.

            * **Temperaturas Altas Constantes:** As linhas no gráfico permanecerão em patamares elevados na maioria dos meses, com menor amplitude entre o ponto mais quente e o mais frio do ano.
            * **Picos de Calor:** Geralmente, os meses entre **setembro e dezembro** (primavera/início do verão) podem exibir os maiores picos de temperatura, especialmente no interior da região.
            * **Influência da Chuva:** Meses com maior volume de chuva (que variam por sub-região) podem ter temperaturas ligeiramente mais amenas devido à nebulosidade.

            **Para identificar meses/anos atípicos (2020-2025):**
            Procure por **picos de temperatura extremos** (linhas muito acima das demais para um mês) que indicam ondas de calor prolongadas. O **verão de 2025**, por exemplo, foi previsto com temperaturas acima da média. Por outro lado, anos sob influência de **La Niña** podem ter temperaturas um pouco mais amenas em alguns períodos devido ao aumento de chuvas.
            """)
        else:
            st.info("Selecione 'Sudeste' ou 'Nordeste' para ver uma análise detalhada dos padrões sazonais de temperatura.")
    # --- Fim da Nova Seção ---

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Certifique-se de que ele está no diretório 'medias' dentro do projeto.")
except KeyError as e:
    st.error(f"Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se os nomes das colunas no CSV estão corretos.")
except Exception as e:
    st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
