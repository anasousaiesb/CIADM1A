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
        "7. Extremos de Radiação"
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
        "1. Qual região do Brasil manteve as temperaturas máximas médias mais elevadas durante a maior parte do ano de 2021? E qual região registrou as temperaturas máximas médias mais baixas, especialmente nos meses de inverno (junho, julho e agosto)?",
        "2. Observando a linha da Região Sul (S), em que mês de 2021 ela atingiu sua temperatura máxima média mais baixa? Compare essa temperatura com a temperatura máxima média da Região Nordeste (NE) no mesmo mês.",
        "3. Tendências de Curto Prazo: Há tendências de aumento/diminuição de temperatura ou precipitação (2020-2025) em alguma região? O que as explica?",
        "4. Diferenças entre Anos: Compare padrões de temperatura e precipitação entre 2020 e 2024 em uma região específica. Isso sugere eventos climáticos ou alta variabilidade?",
        "5. Radiação por Estação: Como a radiação global varia entre regiões no verão e inverno? Como isso se relaciona com a geografia de cada região?",
        "6. Impacto em Setores: Quais regiões seriam mais favoráveis para agricultura de sequeiro e para energia solar, baseando-se nos dados de temperatura, precipitação e radiação?",
        "7. Padrões Sazonais Extremos: Identifique a região com maior amplitude térmica e maior variação de precipitação mensal (2020-2025). Como esses extremos aparecem nos gráficos?",
        "8. Previsões Futuras (Insights Preliminares): Que hipóteses sobre o clima futuro das regiões brasileiras podem ser formuladas com base nesses dados de curto prazo (2020-2025)?",
        "9. Temperatura Sazonal: Descreva os padrões sazonais de temperatura na Região Sudeste e Nordeste (2020-2025) e identifique meses/anos atípicos.",
        "10. Comparação de Chuva: Compare os regimes de precipitação (volumes, picos/secas) entre as Regiões Norte e Sul (2020-2025) e justifique as diferenças.",
        "11. Extremos de Radiação: Identifique regiões e meses com maiores/menores valores de Radiação Global (2020-2025) e sua relevância.",
        "12. Variabilidade Anual: Escolha uma variável e região e analise qual ano (2020-2025) se destaca por valores atipicamente altos/baixos, discutindo as implicações."
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
        <p>Professor: Alexandre Vaz Roriz | Alunos: Ana Sophia, Igor Andrade</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
