import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Análise de Extremos Climáticos 🚨")

# --- CSS PARA ESTILIZAÇÃO APRIMORADA (Aplicado globalmente para ambos os temas) ---
st.markdown("""
<style>
/* Estilos para o tema de "Análise Climática Interativa" */
.stApp {
    background-color: #f0f2f5; /* Fundo cinza claro */
    color: #2C3E50; /* Cor de texto principal */
}
.main-title-1 { /* Título principal do primeiro app */
    font-size: 3.2em;
    font-weight: 700;
    color: #34495E; /* Azul escuro */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle-1 { /* Subtítulo do primeiro app */
    font-size: 1.6em;
    color: #7F8C8D; /* Cinza médio */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section-1 { /* Seção do cabeçalho do primeiro app */
    background: linear-gradient(135deg, #A8DADC 0%, #457B9D 100%); /* Gradiente azul claro */
    padding: 1.8em;
    border-radius: 12px;
    margin-bottom: 2em;
    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    border: 1px solid #1D3557;
}

/* Estilos para o tema de "Análise de Extremos Climáticos" */
.main-title-2 { /* Título principal do segundo app (extremos) */
    font-size: 3.2em;
    font-weight: 700;
    color: #CC0000; /* Vermelho forte para extremos */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle-2 { /* Subtítulo do segundo app (extremos) */
    font-size: 1.6em;
    color: #E65100; /* Laranja escuro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section-2 { /* Seção do cabeçalho do segundo app (extremos) */
    background: linear-gradient(135deg, #FFD180 0%, #FFAB40 100%); /* Gradiente de laranja */
    padding: 1.8em;
    border-radius: 12px;
    margin-bottom: 2em;
    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    border: 1px solid #FF8F00;
}

/* Estilo geral para cabeçalhos de seção */
h2 {
    color: #34495E; /* Cor para subtítulos h2 */
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Caminho relativo ao arquivo CSV
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- FUNÇÃO PARA CARREGAR E PREPARAR OS DADOS (com caching) ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e processa o arquivo de dados climáticos."""
    df = pd.read_csv(caminho)

    # Converte colunas para numérico, tratando erros
    for col in ['Mês', 'Ano', 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
                'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
                'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
                'VENTO, RAJADA MAXIMA (m/s)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['Mês', 'Ano']) # Garante que Mês e Ano não são nulos
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- TÍTULO PRINCIPAL E SUBTÍTULO COM EMOJIS E NOVO ESTILO ---
    st.markdown('<div class="header-section-2">', unsafe_allow_html=True) # Usando a classe do segundo tema
    st.markdown('<h1 class="main-title-2">Análise de Extremos Climáticos Regionais do Brasil 🚨⚠️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-2">Explorando Picos e Vales nos Dados Climáticos (2020-2025) 🌡️💨🌧️</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    Desvende os recordes e as condições mais severas registradas em diversas regiões do Brasil!
    Esta ferramenta permite identificar os **maiores valores** de temperatura, precipitação e rajadas de vento,
    além das **menores temperaturas**, oferecendo um panorama das condições climáticas mais extremas.
    """)

    # --- INTERFACE DO USUÁRIO ---
    st.sidebar.header("Filtros de Análise ⚙️")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())

    # Dropdown para selecionar a variável de extremo
    variaveis_extremo = {
        'Temperatura Máxima (°C)': 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'Temperatura Mínima (°C)': 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Rajada Máxima de Vento (m/s)': 'VENTO, RAJADA MAXIMA (m/s)'
    }
    nome_var_extremo = st.sidebar.selectbox("Selecione a Variável de Extremo:", list(variaveis_extremo.keys()))
    coluna_var_extremo = variaveis_extremo[nome_var_extremo]
    
    # Verifica se a coluna selecionada realmente existe no DataFrame
    if coluna_var_extremo not in df_unificado.columns:
        st.error(f"❌ **Erro:** A coluna '{coluna_var_extremo}' para a variável '{nome_var_extremo}' não foi encontrada no seu arquivo CSV. Por favor, verifique se os nomes das colunas estão corretos. 🛑")
        st.stop()

    unidade_var_extremo = nome_var_extremo.split('(')[-1].replace(')', '') if '(' in nome_var_extremo else ''

    # Slider para selecionar os anos
    ano_inicio, ano_fim = st.sidebar.select_slider(
        "Selecione o Intervalo de Anos:",
        options=anos.astype(int), # Garante que os anos são inteiros para o slider
        value=(int(min(anos)), int(max(anos)))
    )
    df_filtrado_ano = df_unificado[(df_unificado['Ano'] >= ano_inicio) & (df_unificado['Ano'] <= ano_fim)]

    st.markdown("---")

    # --- ANÁLISE DE EXTREMOS CLIMÁTICOS POR REGIÃO ---
    st.header(f"Recordes de {nome_var_extremo} por Região ({ano_inicio}-{ano_fim}) 📈")
    st.write(f"""
    Esta tabela revela os **valores mais extremos** (máximos ou mínimos, dependendo da variável) registrados para **{nome_var_extremo.lower()}** em cada região, dentro do período de **{ano_inicio} a {ano_fim}**.
    Explore para identificar as regiões que experimentaram as condições mais desafiadoras!
    """)

    # Agrupando por região para encontrar os valores extremos
    if "Mínima" in nome_var_extremo: # Para temperatura mínima, queremos o menor valor
        df_extremos_regionais = df_filtrado_ano.groupby('Regiao')[coluna_var_extremo].min().reset_index()
        # Ordenar para mostrar o menor valor primeiro para "Mínima"
        df_extremos_regionais = df_extremos_regionais.sort_values(by=f'{coluna_var_extremo}', ascending=True)
    else: # Para as outras variáveis, queremos o maior valor
        df_extremos_regionais = df_filtrado_ano.groupby('Regiao')[coluna_var_extremo].max().reset_index()
        # Ordenar para mostrar o maior valor primeiro
        df_extremos_regionais = df_extremos_regionais.sort_values(by=f'{coluna_var_extremo}', ascending=False)


    if not df_extremos_regionais.empty:
        # Renomeando a coluna para melhor exibição
        df_extremos_regionais.rename(columns={coluna_var_extremo: f'{nome_var_extremo} Extremo'}, inplace=True)
        
        st.dataframe(df_extremos_regionais.set_index('Regiao').style.format("{:.2f}").highlight_max(axis=0, color='lightcoral').highlight_min(axis=0, color='lightblue'))

        # Gráfico de barras para os extremos
        fig_extremo, ax_extremo = plt.subplots(figsize=(12, 6))
        
        # Cores dinâmicas baseadas na variável
        if "Temperatura Máxima" in nome_var_extremo:
            bar_color = '#E74C3C' # Vermelho para calor extremo
        elif "Temperatura Mínima" in nome_var_extremo:
            bar_color = '#3498DB' # Azul para frio extremo
        elif "Precipitação Total" in nome_var_extremo:
            bar_color = '#2ECC71' # Verde para chuva
        elif "Rajada Máxima de Vento" in nome_var_extremo:
            bar_color = '#9B59B6' # Roxo para vento
        else:
            bar_color = '#FF7043' # Cor padrão

        ax_extremo.bar(df_extremos_regionais['Regiao'], df_extremos_regionais[f'{nome_var_extremo} Extremo'], color=bar_color, alpha=0.9)
        ax_extremo.set_title(f'{nome_var_extremo} Extremo por Região', fontsize=18, fontweight='bold', color='#34495E')
        ax_extremo.set_xlabel('Região', fontsize=14, color='#34495E')
        ax_extremo.set_ylabel(f'{nome_var_extremo} ({unidade_var_extremo})', fontsize=14, color='#34495E')
        ax_extremo.tick_params(axis='x', rotation=45, labelsize=10)
        ax_extremo.tick_params(axis='y', labelsize=10)
        ax_extremo.grid(axis='y', linestyle='--', alpha=0.7, color='#BDC3C7')
        ax_extremo.set_facecolor('#F8F9FA') # Fundo do gráfico
        plt.tight_layout()
        st.pyplot(fig_extremo)

        st.markdown("---")

        st.header("Insights e Potenciais Impactos dos Extremos Climáticos 🤔")
        st.warning("🚨 **Importante:** As análises e hipóteses abaixo são baseadas nos dados disponíveis para o período de 2020-2025. Para uma compreensão completa das tendências e impactos das mudanças climáticas, estudos com séries históricas mais longas e modelagem climática são essenciais.")

        # Gerando insights dinâmicos
        if not df_extremos_regionais.empty:
            # Pega a primeira linha da tabela já ordenada para o "extremo" principal
            extremo_data = df_extremos_regionais.iloc[0]
            regiao_extremo = extremo_data['Regiao']
            valor_extremo = extremo_data[f'{nome_var_extremo} Extremo']
            
            if "Temperatura Máxima" in nome_var_extremo:
                st.markdown(f"""
                ### O Calor no Topo! ☀️
                A Região de **{regiao_extremo}** registrou a **temperatura máxima mais alta** ({valor_extremo:.2f} {unidade_var_extremo}) no período selecionado.
                * **Impacto Potencial:** Este dado acende um alerta para **ondas de calor mais frequentes e intensas**. Isso pode sobrecarregar sistemas de saúde, aumentar a demanda por energia (ar-condicionado) e impactar a produtividade agrícola e urbana.
                * **Consequência:** Cidades e áreas rurais podem precisar de estratégias de mitigação do calor, como aumento de áreas verdes e infraestrutura mais resiliente.
                """)
            elif "Temperatura Mínima" in nome_var_extremo:
                st.markdown(f"""
                ### O Frio que Surpreende! ❄️
                A Região de **{regiao_extremo}** alcançou a **temperatura mínima mais baixa** ({valor_extremo:.2f} {unidade_var_extremo}) no período.
                * **Impacto Potencial:** Períodos de frio intenso podem levar a **perdas agrícolas por geadas**, aumento do consumo de energia para aquecimento e riscos à saúde de populações vulneráveis.
                * **Consequência:** A atenção deve se voltar para a proteção de lavouras sensíveis e a garantia de aquecimento adequado em comunidades afetadas.
                """)
            elif "Precipitação Total" in nome_var_extremo:
                st.markdown(f"""
                ### Chuva Intensa: Alerta Máximo! 💧
                A Região de **{regiao_extremo}** acumulou o **maior volume de precipitação** ({valor_extremo:.2f} {unidade_var_extremo}) em um mês no período.
                * **Impacto Potencial:** volumes extremos de chuva aumentam drasticamente o risco de **inundações, deslizamentos de terra** e transbordamento de rios, afetando infraestrutura e vidas.
                * **Consequência:** É crucial reforçar o planejamento urbano, sistemas de drenagem e alertas precoces à população em áreas de risco.
                """)
            elif "Rajada Máxima de Vento" in nome_var_extremo:
                st.markdown(f"""
                ### Ventos Fortes: Força da Natureza! 🌬️
                A Região de **{regiao_extremo}** registrou a **rajada máxima de vento mais forte** ({valor_extremo:.2f} {unidade_var_extremo}) no período.
                * **Impacto Potencial:** Ventos de alta velocidade podem causar **danos severos a edifícios, árvores, redes elétricas e telecomunicações**, levando a interrupções e riscos à segurança.
                * **Consequência:** A necessidade de estruturas mais robustas e planos de resposta a emergências para eventos de vento extremo torna-se evidente.
                """)
    else:
        st.info("Não foi possível gerar insights sobre extremos. Ajuste seus filtros e tente novamente! 🙁")

except FileNotFoundError:
    st.error(f"❌ **Erro:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e a localização do arquivo. 📁")
except KeyError as e:
    st.error(f"⚠️ **Erro de Coluna:** A coluna essencial '{e}' não foi encontrada no arquivo CSV. Verifique se o seu arquivo contém todos os dados necessários para a análise. 🧐")
except Exception as e:
    st.error(f"💥 **Ocorreu um erro inesperado!** Parece que algo deu errado durante o processamento. Por favor, tente novamente. Detalhes técnicos: `{e}` 🐛")

st.markdown("---")
st.markdown("✨ Qual outro aspecto do clima você gostaria de investigar mais a fundo? Sua curiosidade nos impulsiona! ✨")
