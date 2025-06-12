import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- CONFIGURAÇÕES INICIAIS DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Extremos Climáticos 🚨")

# --- CSS para estilização aprimorada do título e subtítulo (mantido e aprimorado) ---
st.markdown("""
<style>
.stApp {
    background-color: #f0f2f5; /* Fundo cinza claro */
    color: #2C3E50; /* Cor de texto principal */
}
/* Estilos para o tema de "Análise de Extremos Climáticos" */
.main-title-extreme { /* Título principal dos extremos */
    font-size: 3.2em;
    font-weight: 700;
    color: #CC0000; /* Vermelho forte para extremos */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle-extreme { /* Subtítulo dos extremos */
    font-size: 1.6em;
    color: #E65100; /* Laranja escuro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section-extreme { /* Seção do cabeçalho dos extremos */
    background: linear-gradient(135deg, #FFD180 0%, #FFAB40 100%); /* Gradiente de laranja */
    padding: 1.8em;
    border-radius: 12px;
    margin-bottom: 2em;
    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    border: 1px solid #FF8F00;
}
/* Estilo para st.metric */
[data-testid="stMetricValue"] {
    font-size: 2.5em;
    font-weight: bold;
    color: #CC0000; /* Vermelho vibrante para o valor */
}
[data-testid="stMetricLabel"] {
    font-size: 1.2em;
    color: #E65100; /* Laranja para o rótulo */
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
                'VENTO, RAJADA MAXIMA (m/s)',
                'RADIACAO GLOBAL (Kj/m²)']: # Adicionado radiação caso precise
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['Mês', 'Ano']) # Garante que Mês e Ano não são nulos
    return df

# --- CARREGAMENTO DOS DADOS E TRATAMENTO DE ERROS ---
try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- TÍTULO PRINCIPAL E SUBTÍTULO COM EMOJIS E ESTILO CUSTOMIZADO ---
    st.markdown('<div class="header-section-extreme">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title-extreme">Análise de Extremos Climáticos Regionais do Brasil 🚨⚠️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-extreme">Descubra os Picos e Vales nos Dados Climáticos (2020-2025) 🌡️💨🌧️</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    Prepare-se para uma jornada pelos **recordes climáticos** do Brasil! Esta ferramenta interativa
    permite que você identifique e visualize os **valores mais altos e mais baixos**
    de diversas variáveis climáticas, como temperatura, precipitação e rajadas de vento.
    Descubra quais regiões enfrentaram as condições mais **extremas** no período de 2020 a 2025.
    """)

    # --- INTERFACE DO USUÁRIO NA BARRA LATERAL ---
    st.sidebar.header("Filtros de Análise ⚙️")
    
    regioes = sorted(df_unificado['Regiao'].unique())
    anos = sorted(df_unificado['Ano'].unique())

    # Dropdown para selecionar a variável de extremo
    variaveis_extremo = {
        'Temperatura Máxima (°C)': 'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'Temperatura Mínima (°C)': 'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
        'Precipitação Total (mm)': 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
        'Rajada Máxima de Vento (m/s)': 'VENTO, RAJADA MAXIMA (m/s)'
        # 'Radiação Global (Kj/m²)': 'RADIACAO GLOBAL (Kj/m²)' # Se quiser incluir radiação
    }
    nome_var_extremo = st.sidebar.selectbox("Escolha a Variável de Extremo para Explorar:", list(variaveis_extremo.keys()))
    coluna_var_extremo = variaveis_extremo[nome_var_extremo]
    
    # Verifica se a coluna selecionada realmente existe no DataFrame
    if coluna_var_extremo not in df_unificado.columns:
        st.error(f"❌ **Erro:** A coluna '{coluna_var_extremo}' para a variável '{nome_var_extremo}' não foi encontrada no seu arquivo CSV. Por favor, verifique os nomes das colunas. 🛑")
        st.stop()

    unidade_var_extremo = nome_var_extremo.split('(')[-1].replace(')', '') if '(' in nome_var_extremo else ''

    # Slider para selecionar os anos
    ano_inicio, ano_fim = st.sidebar.select_slider(
        "Defina o Intervalo de Anos:",
        options=anos.astype(int),
        value=(int(min(anos)), int(max(anos)))
    )
    df_filtrado_ano = df_unificado[(df_unificado['Ano'] >= ano_inicio) & (df_unificado['Ano'] <= ano_fim)]

    st.markdown("---")

    # --- DESTAQUE DO EXTREMO GERAL (st.metric) ---
    st.subheader(f"🏆 O Recorde Geral de {nome_var_extremo} no Período Selecionado:")
    
    if "Mínima" in nome_var_extremo:
        overall_extreme_value = df_filtrado_ano[coluna_var_extremo].min()
        overall_extreme_row = df_filtrado_ano.loc[df_filtrado_ano[coluna_var_extremo].idxmin()]
        metric_label = f"Mínimo Histórico de {nome_var_extremo}"
    else:
        overall_extreme_value = df_filtrado_ano[coluna_var_extremo].max()
        overall_extreme_row = df_filtrado_ano.loc[df_filtrado_ano[coluna_var_extremo].idxmax()]
        metric_label = f"Máximo Histórico de {nome_var_extremo}"

    if not pd.isna(overall_extreme_value):
        st.metric(label=metric_label, value=f"{overall_extreme_value:.2f} {unidade_var_extremo}")
        st.info(f"Ocorreu em **{overall_extreme_row['Regiao']}** no mês {int(overall_extreme_row['Mês'])} de {int(overall_extreme_row['Ano'])}.")
    else:
        st.info("Não foi possível determinar o valor extremo geral para a seleção atual. 🙁")

    st.markdown("---")

    # --- ANÁLISE DE EXTREMOS CLIMÁTICOS POR REGIÃO ---
    st.header(f"Explorando os Extremos de {nome_var_extremo} por Região ({ano_inicio}-{ano_fim}) 📊")
    st.write(f"""
    A tabela e o gráfico abaixo revelam os **valores mais extremos** (máximos ou mínimos) registrados para
    **{nome_var_extremo.lower()}** em cada região do Brasil, dentro do período de **{ano_inicio} a {ano_fim}**.
    Observe as variações e identifique as regiões que se destacam por suas condições climáticas mais severas.
    """)

    # Agrupando por região para encontrar os valores extremos
    if "Mínima" in nome_var_extremo:
        df_extremos_regionais = df_filtrado_ano.groupby('Regiao')[coluna_var_extremo].min().reset_index()
        df_extremos_regionais = df_extremos_regionais.sort_values(by=coluna_var_extremo, ascending=True)
    else:
        df_extremos_regionais = df_filtrado_ano.groupby('Regiao')[coluna_var_extremo].max().reset_index()
        df_extremos_regionais = df_extremos_regionais.sort_values(by=coluna_var_extremo, ascending=False)

    if not df_extremos_regionais.empty:
        # Renomeando a coluna para melhor exibição
        df_extremos_regionais.rename(columns={coluna_var_extremo: f'{nome_var_extremo} Extremo'}, inplace=True)
        
        # Estilização da tabela com destaque para valores extremos
        st.dataframe(df_extremos_regionais.set_index('Regiao').style.format("{:.2f}").background_gradient(cmap='YlOrRd' if "Mínima" not in nome_var_extremo else 'Blues_r'))

        # Gráfico de barras para os extremos
        fig_extremo, ax_extremo = plt.subplots(figsize=(12, 7)) # Aumentado um pouco a altura
        
        # Cores dinâmicas e mais vibrantes baseadas na variável
        if "Temperatura Máxima" in nome_var_extremo:
            bar_color = '#E74C3C' # Vermelho intenso para calor extremo
        elif "Temperatura Mínima" in nome_var_extremo:
            bar_color = '#3498DB' # Azul profundo para frio extremo
        elif "Precipitação Total" in nome_var_extremo:
            bar_color = '#2ECC71' # Verde vibrante para chuva
        elif "Rajada Máxima de Vento" in nome_var_extremo:
            bar_color = '#9B59B6' # Roxo para vento
        else:
            bar_color = '#FF7043' # Cor padrão laranja/vermelho

        ax_extremo.bar(df_extremos_regionais['Regiao'], df_extremos_regionais[f'{nome_var_extremo} Extremo'], color=bar_color, alpha=0.9, edgecolor='black', linewidth=0.7)
        ax_extremo.set_title(f'Recordes de {nome_var_extremo} por Região ({ano_inicio}-{ano_fim})', fontsize=20, fontweight='bold', color='#34495E')
        ax_extremo.set_xlabel('Região', fontsize=15, color='#34495E')
        ax_extremo.set_ylabel(f'{nome_var_extremo} ({unidade_var_extremo})', fontsize=15, color='#34495E')
        ax_extremo.tick_params(axis='x', rotation=45, labelsize=12)
        ax_extremo.tick_params(axis='y', labelsize=12)
        ax_extremo.grid(axis='y', linestyle='--', alpha=0.7, color='#BDC3C7')
        ax_extremo.set_facecolor('#F8F9FA') # Fundo do gráfico
        plt.tight_layout()
        st.pyplot(fig_extremo)

        st.markdown("---")

        st.header("Insights e Hipóteses sobre Extremos Climáticos 🤔")
        st.warning("🚨 **Atenção:** As análises e hipóteses abaixo são exploratórias e baseadas em um período de dados limitado (2020-2025). Para conclusões definitivas sobre mudanças climáticas e eventos extremos, são necessárias séries históricas de dados muito mais longas e estudos aprofundados.")

        # --- Insights Dinâmicos dentro de Expanders ---
        if not df_extremos_regionais.empty:
            if "Temperatura Máxima" in nome_var_extremo:
                top_region = df_extremos_regionais.iloc[0]
                with st.expander(f"✨ **Desvende o Recorde de Calor: {top_region['Regiao']}**"):
                    st.markdown(f"""
                    A Região de **{top_region['Regiao']}** foi a que registrou a **temperatura máxima mais alta** ({top_region[f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) no período selecionado.
                    * **Potencial Impacto:** Esse cenário pode indicar que essa região está mais suscetível a **ondas de calor prolongadas e intensas**. Isso sobrecarrega os sistemas de saúde, aumenta a demanda por energia para refrigeração e impacta diretamente a produtividade na agricultura e no ambiente urbano.
                    * **O que significa?** Cidades e áreas rurais podem precisar de estratégias urgentes de adaptação ao calor, como a expansão de áreas verdes, melhorias na infraestrutura e sistemas de alerta de saúde pública.
                    """)
            
            elif "Temperatura Mínima" in nome_var_extremo:
                top_region = df_extremos_regionais.iloc[0] # Para mínima, a primeira é a menor
                with st.expander(f"🥶 **Onde o Frio Atingiu seu Ponto Mais Baixo: {top_region['Regiao']}**"):
                    st.markdown(f"""
                    A Região de **{top_region['Regiao']}** alcançou a **temperatura mínima mais baixa** ({top_region[f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) no período.
                    * **Potencial Impacto:** Períodos de frio extremo podem causar **perdas significativas na agricultura devido a geadas**, aumentar o consumo de energia para aquecimento e representar riscos graves à saúde de populações mais vulneráveis.
                    * **O que significa?** É fundamental que as regiões com esses recordes preparem suas lavouras e infraestruturas para proteger-se contra eventos de frio intenso e garantir o bem-estar de seus habitantes.
                    """)
            
            elif "Precipitação Total" in nome_var_extremo:
                top_region = df_extremos_regionais.iloc[0]
                with st.expander(f"🌊 **Recorde de Chuva: A Força da Água em {top_region['Regiao']}**"):
                    st.markdown(f"""
                    A Região de **{top_region['Regiao']}** registrou o **maior volume de precipitação** ({top_region[f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) em um único mês no período analisado.
                    * **Potencial Impacto:** Volumes tão extremos de chuva elevam drasticamente o risco de **inundações repentinas, deslizamentos de terra e transbordamento de rios**, impactando severamente infraestruturas e a segurança da vida humana.
                    * **O que significa?** Planejamento urbano resiliente, sistemas de drenagem eficientes e alertas precoces à população são cruciais para mitigar os riscos em áreas suscetíveis a chuvas torrenciais.
                    """)
            
            elif "Rajada Máxima de Vento" in nome_var_extremo:
                top_region = df_extremos_regionais.iloc[0]
                with st.expander(f"💨 **Onde o Vento Soprou Mais Forte: {top_region['Regiao']}**"):
                    st.markdown(f"""
                    A Região de **{top_region['Regiao']}** experimentou a **rajada máxima de vento mais forte** ({top_region[f'{nome_var_extremo} Extremo']:.2f} {unidade_var_extremo}) no período.
                    * **Potencial Impacto:** Ventos de alta velocidade podem causar **danos severos a edificações, quedas de árvores, interrupções em redes elétricas e de comunicação**, e colocar a segurança pública em risco.
                    * **O que significa?** Regiões com esses registros necessitam de infraestrutura mais robusta e planos de contingência bem definidos para proteger bens e pessoas durante eventos de vento extremo.
                    """)

    else:
        st.info("Não há dados de extremos disponíveis para a variável e o período selecionados. 😔 Tente ajustar os filtros para revelar mais informações!")

except FileNotFoundError:
    st.error(f"❌ **Erro Crítico:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e a localização do arquivo para continuar a análise. 📁")
except KeyError as e:
    st.error(f"⚠️ **Erro de Coluna:** A coluna essencial '{e}' não foi encontrada no seu arquivo CSV. Verifique se os nomes das colunas correspondem exatamente aos esperados. 🧐")
except Exception as e:
    st.error(f"💥 **Ocorreu um erro inesperado!** Lamentamos, mas algo deu errado durante o processamento dos dados. Por favor, tente novamente ou entre em contato se o problema persistir. Detalhes técnicos: `{e}` 🐛")

st.markdown("---")
st.markdown("✨ Esperamos que esta análise dos extremos climáticos tenha sido esclarecedora! Qual outro mistério climático você gostaria de desvendar em seguida? Sua curiosidade é o nosso combustível! ✨")
