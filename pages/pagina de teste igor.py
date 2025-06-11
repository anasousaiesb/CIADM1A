import streamlit as st

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Introdução - Análise Climática",
        page_icon="🌦️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS incorporado para estilização
    st.markdown("""
    <style>
    .header-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .topic-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #4e79a7;
    }
    .question-card {
        padding: 1.2rem;
        border-radius: 8px;
        background-color: #f8f9fa;
        margin-bottom: 0.8rem;
        border-left: 3px solid #e15759;
    }
    .highlight-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1.5rem 0;
    }
    .topic-title {
        color: #2b5876;
        font-weight: 600;
    }
    .question-text {
        color: #555555;
        font-size: 0.95em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho
    st.markdown('<div class="header-section">', unsafe_allow_html=True)
    st.title("Sistema de Análise Climática")
    st.subheader("Dados do INMET (2020-2025)")
    st.markdown("""
    <p style="font-size:1.1em">Este sistema permite a análise de padrões climáticos no Brasil, com foco em temperatura, 
    precipitação e radiação global, utilizando dados do Instituto Nacional de Meteorologia.</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção de Tópicos de Análise
    st.header("📌 Tópicos de Análise Disponíveis")
    
    # Tópicos da imagem
    topics = [
        "1. Análise de Radiação Global em 2020",
        "2. Qualidade dos Dados e Correlações Climáticas",
        "3. Padrões Sazonais Extremos",
        "4. Radiação Global por Estação",
        "5. Comparação de Chuva entre Regiões Norte e Sul",
        "6. Temperatura Sazonal",
        "7. Extremos de Radiação",
        "8. Comparação de Chuva"
    ]
    
    for topic in topics:
        st.markdown(f"""
        <div class="topic-card">
            <h4 class="topic-title">{topic}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de Perguntas de Pesquisa
    st.header("🔍 Questões-Chave da Pesquisa")
    
    questions = [
        Análise de Radiação Global em 2020 - 2025
[
Considerando a série temporal de radiação global de 2020 a 2025, quais são as tendências observadas (aumento, diminuição, estabilidade) e quais anomalias (picos ou vales significativos) podem ser identificadas para o período, e como elas se comparam com anos anteriores?
Qualidade dos Dados e Correlações Climáticas

Ao avaliar a qualidade dos dados de radiação global para o período, que incertezas ou lacunas foram identificadas e como essas incertezas podem afetar as correlações encontradas entre a radiação global e outras variáveis climáticas (como temperatura, nebulosidade ou umidade)?
Análise de Extremos

Quais foram os eventos de radiação global extrema (máximos e mínimos históricos ou significativamente desviantes da média) observados entre 2020 e 2025, e houve alguma correlação desses eventos com outros fenômenos climáticos extremos, como ondas de calor ou períodos de seca/chuva intensa?
Facetado por Região e Variável

Ao segmentar a análise de radiação global por diferentes regiões geográficas e variáveis climáticas (ex: tipo de vegetação, altitude), quais são as diferenças mais marcantes no comportamento da radiação global entre as regiões, e como essas diferenças se relacionam com as características ambientais locais?
Contrastando o Clima

Considerando as diferenças climáticas regionais, como a radiação global média e sua variabilidade se comportam em regiões com climas distintos (ex: tropical úmido vs. semiárido) e como essas variações podem ser explicadas pela interação com outros elementos climáticos como nebulosidade e umidade?
Temperatura Sazonal

Como a radiação global sazonal se correlaciona com os padrões de temperatura sazonal em diferentes regiões, e qual o papel da radiação na explicação das variações de temperatura observadas ao longo das estações, considerando o balanço de energia superficial?
Médias Mensais Regionais

Ao analisar as médias mensais regionais de radiação global, quais são os meses de maior e menor incidência em cada região e como esses padrões mensais se comparam entre si, revelando particularidades climáticas regionais ao longo do ano?
Comparação de Chuva

Existe uma relação inversa ou direta entre a radiação global e os padrões de precipitação (chuva) em diferentes regiões e em que escala temporal (diária, mensal, sazonal) essa relação é mais evidente, e quais são os mecanismos físicos que explicam essa interação?
    ]   
    for i, question in enumerate(questions, start=1):
        st.markdown(f"""
        <div class="question-card">
            <p class="question-text"><strong>{i}.</strong> {question}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de informações adicionais
    st.markdown("""
    <div class="highlight-box">
        <h4>📌 Como Utilizar o Sistema</h4>
        <p>1. Navegue pelos tópicos de análise no menu lateral</p>
        <p>2. Selecione os parâmetros desejados para cada visualização</p>
        <p>3. Explore os gráficos interativos e tabelas de dados</p>
        <p>4. Utilize os filtros para focar em regiões ou períodos específicos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Rodapé
    st.write("---")
    st.markdown("""
    <div style="text-align: center; color: #666666; font-size: 0.9em;">
        <p>Sistema desenvolvido para o projeto CIADM1A-CIA001-20251</p>
        <p>Professor: Alexandre Vaz Roriz | Alunos: Ana Sophia e Igor Andrade</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
