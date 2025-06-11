import streamlit as st

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Início - Análise Climática Brasil",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS incorporado para estilização aprimorada
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .stApp {
        background-color: #f4f7fa; /* Fundo mais suave */
    }

    .main-header-container {
        background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%); /* Gradiente verde vibrante */
        padding: 3rem 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .main-header-container h1 {
        color: white;
        font-weight: 700;
        font-size: 3.2em;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header-container h3 {
        color: #e0e0e0;
        font-weight: 400;
        font-size: 1.5em;
    }
    .main-header-container p {
        color: #e0e0e0;
        font-size: 1.1em;
        max-width: 800px;
        margin: 1rem auto 0;
        line-height: 1.6;
    }

    .section-title {
        color: #2e7d32; /* Verde mais escuro para títulos de seção */
        font-weight: 600;
        font-size: 2em;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #a5d6a7;
        padding-bottom: 0.5rem;
    }

    .topic-card, .question-card {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .topic-card:hover, .question-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }
    .topic-card {
        border-left: 6px solid #4CAF50; /* Verde principal */
    }
    .question-card {
        border-left: 6px solid #FFC107; /* Amarelo para perguntas */
    }
    
    .topic-title {
        color: #388E3C; /* Verde escuro para título do tópico */
        font-weight: 700;
        font-size: 1.3em;
        margin-bottom: 0.5rem;
    }
    .question-text {
        color: #424242;
        font-size: 1em;
        line-height: 1.6;
    }
    .question-text strong {
        color: #FF8F00; /* Laranja mais vibrante para números de pergunta */
    }

    .highlight-box {
        background-color: #e8f5e9; /* Fundo verde claro */
        padding: 1.8rem;
        border-radius: 12px;
        margin: 2.5rem 0;
        border: 1px solid #c8e6c9;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .highlight-box h4 {
        color: #2e7d32;
        font-size: 1.5em;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .highlight-box p {
        color: #424242;
        font-size: 1em;
        margin-bottom: 0.5rem;
    }

    .footer-section {
        text-align: center;
        color: #757575;
        font-size: 0.9em;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho principal com gradiente e descrição
    st.markdown('<div class="main-header-container">', unsafe_allow_html=True)
    st.markdown("<h1>Análise Climática no Brasil 🇧🇷</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Explorando Dados do INMET (2020-2025)</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p>Este sistema interativo foi desenvolvido para aprofundar o estudo dos padrões climáticos no Brasil, com foco em variáveis cruciais como <b>radiação global</b>, <b>temperatura</b> e <b>precipitação</b>. Utilize nossos recursos visuais e ferramentas de filtragem para desvendar insights valiosos sobre o clima em diferentes regiões brasileiras.</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ---
    
    # Seção de Tópicos de Análise
    st.markdown('<h2 class="section-title">✨ Nossas Áreas de Análise</h2>', unsafe_allow_html=True)
    
    # Tópicos da imagem
    topics = [
        "1. Radiação Global: Tendências e Anomalias (2020-2025)",
        "2. Qualidade dos Dados e Correlações Climáticas",
        "3. Padrões de Extremos Climáticos: Análise Detalhada",
        "4. Radiação Global Facetada por Região e Variável",
        "5. Contrastando o Clima em Diferentes Regiões",
        "6. Análise da Temperatura Sazonal",
        "7. Médias Mensais Regionais de Radiação Global",
        "8. Comparativo de Padrões de Chuva"
    ]
    
    col1, col2 = st.columns(2) # Usando colunas para organizar os cards
    
    for i, topic in enumerate(topics):
        if i % 2 == 0: # Coloca nos cards da coluna 1
            with col1:
                st.markdown(f"""
                <div class="topic-card">
                    <p class="topic-title">{topic}</p>
                </div>
                """, unsafe_allow_html=True)
        else: # Coloca nos cards da coluna 2
            with col2:
                st.markdown(f"""
                <div class="topic-card">
                    <p class="topic-title">{topic}</p>
                </div>
                """, unsafe_allow_html=True)
                
    # ---
    
    # Seção de Perguntas de Pesquisa
    st.markdown('<h2 class="section-title">💡 Questões-Chave que Buscamos Responder</h2>', unsafe_allow_html=True)
    
    questions = [
        "1. Considerando a série temporal de radiação global de 2020 a 2025, quais **tendências** (aumento, diminuição, estabilidade) e **anomalias** (picos ou vales significativos) podem ser identificadas para o período? Como elas se comparam com anos anteriores?",
        "2. Ao avaliar a **qualidade dos dados** de radiação global, que incertezas ou lacunas foram identificadas? Como essas incertezas podem afetar as correlações com outras variáveis climáticas (temperatura, nebulosidade, umidade)?",
        "3. Quais foram os **eventos de radiação global extrema** (máximos e mínimos históricos) observados entre 2020 e 2025? Houve alguma correlação desses eventos com outros fenômenos climáticos extremos, como ondas de calor ou períodos de seca/chuva intensa?",
        "4. Ao segmentar a análise de radiação global por **diferentes regiões geográficas e variáveis** (ex: tipo de vegetação, altitude), quais são as diferenças mais marcantes no comportamento da radiação? Como elas se relacionam com as características ambientais locais?",
        "5. Considerando as **diferenças climáticas regionais**, como a radiação global média e sua variabilidade se comportam em climas distintos (ex: tropical úmido vs. semiárido)? Como essas variações podem ser explicadas pela interação com nebulosidade e umidade?",
        "6. Como a **radiação global sazonal** se correlaciona com os padrões de temperatura sazonal em diferentes regiões? Qual o papel da radiação na explicação das variações de temperatura ao longo das estações, considerando o balanço de energia superficial?",
        "7. Ao analisar as **médias mensais regionais de radiação global**, quais são os meses de maior e menor incidência em cada região? Como esses padrões mensais se comparam entre si, revelando particularidades climáticas regionais?",
        "8. Existe uma **relação inversa ou direta** entre a radiação global e os padrões de precipitação (chuva) em diferentes regiões? Em que escala temporal (diária, mensal, sazonal) essa relação é mais evidente, e quais os mecanismos físicos que a explicam?"
    ]
    
    for i, question in enumerate(questions):
        st.markdown(f"""
        <div class="question-card">
            <p class="question-text"><strong>{i+1}.</strong> {question}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ---
    
    # Seção de informações adicionais
    st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    st.markdown("<h4>🚀 Guia Rápido: Como Navegar no Sistema</h4>", unsafe_allow_html=True)
    st.markdown("""
    <ul>
        <li>1. <b>Navegue</b> pelos tópicos de análise utilizando o menu lateral esquerdo.</li>
        <li>2. <b>Selecione</b> os parâmetros desejados para cada visualização (filtros de data, região, variáveis, etc.).</li>
        <li>3. <b>Explore</b> os gráficos interativos, mapas e tabelas de dados que fornecem insights detalhados.</li>
        <li>4. <b>Utilize os filtros</b> para refinar sua pesquisa e focar em aspectos específicos do clima brasileiro.</li>
        <li>5. <b>Interaja</b> com os elementos para uma experiência de análise dinâmica e personalizada.</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div class="footer-section">
        <p>📊 Projeto CIADM1A-CIA001-20251 | Professor: Alexandre Vaz Roriz</p>
        <p>Desenvolvido por: Ana Sophia e Igor Andrade</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
