# 🏠_Home.py
import streamlit as st

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Análises de Dados - CIADM1A",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS incorporado para estilização mínima
    st.markdown("""
    <style>
    .custom-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        height: 160px; /* Altura fixa para melhor alinhamento dos cards */
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Alinha conteúdo no topo */
    }
    .custom-card h4 {
        font-size: 1.1em; 
        margin-bottom: 0.5rem; /* Espaço abaixo do título do card */
    }
    .custom-card p {
        font-size: 0.9em; 
        color:#555555; /* Cor de texto um pouco mais escura para melhor leitura */
    }
    .highlight-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .stApp [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem; /* Adiciona um pouco de padding no topo da sidebar */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho
    st.title("Projeto de Análise de Dados")
    st.subheader("CIADM1A-CIA001-20251")
    
    st.write("---")

    # Seção de informações da equipe em colunas
    col_prof, col_alunos_intro = st.columns([1, 2])

    with col_prof:
        st.subheader("Professor:")
        st.markdown("""
        <div class="custom-card" style="height: auto; justify-content: center; text-align: center;">
            Alexandre Vaz Roriz
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Alunos:")
        st.markdown("""
        <div class="custom-card" style="height: auto; justify-content: center; text-align: center;">
            Ana Sophia<br>
            Igor Andrade
        </div>
        """, unsafe_allow_html=True)

    with col_alunos_intro:
        with st.expander("📌 Introdução ao Projeto", expanded=True):
            st.markdown("""
            Este projeto apresenta uma coleção de análises de dados desenvolvidas como parte da disciplina de Introdução à Ciência de Dados.
            Exploramos diferentes conjuntos de dados e técnicas para extrair informações e apresentar visualizações interativas.
            
            O objetivo é aplicar os conceitos aprendidos para analisar, interpretar e comunicar resultados a partir de dados diversos.

            <div class="highlight-box">
                <p><strong>💡 Dica:</strong> Navegue pelo menu lateral para acessar cada tópico da análise detalhada.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.subheader("Visão Geral das Análises Disponíveis")
    st.write("Explore os diferentes módulos de análise disponíveis no menu lateral. Abaixo, um resumo dos tópicos:")
    
    sections = [
        ("☀️", "Análise de Radiação Global em 2020", "Detalhes da radiação global no ano de 2020."),
        ("📅", "Análise Anual", "Estudos e comparações baseados em dados anuais."),
        ("🗺️", "Facetado por Região e Variável", "Dados segmentados por região e múltiplas variáveis."),
        ("📈", "Médias Mensais por Estado", "Consulta de médias mensais com filtro por estado."),
        ("📊", "Médias Mensais Regionais (2020-2025)", "Médias por região para o período 2020-2025."),
        ("📄", "Página 2", "Conteúdo ou análise adicional."),
        ("🧪", "Testes", "Demonstrações e testes de funcionalidades.")
    ]
    
    num_cols = 3 # Ajustado para 3 colunas para melhor visualização dos 7 cards
    for i in range(0, len(sections), num_cols):
        cols = st.columns(num_cols)
        for j, (icon, title, desc) in enumerate(sections[i:i+num_cols]):
            if i + j < len(sections): # Garante que não tentamos acessar um índice fora dos limites para a última linha
                with cols[j]:
                    st.markdown(f"""
                    <div class="custom-card">
                        <h4>{icon} {title}</h4>
                        <p>{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.write("---")
    st.caption("Trabalho desenvolvido para a disciplina de Introdução à Ciência de Dados - 2025/1")
    st.caption("Fontes de dados variadas, conforme cada análise.") 

if __name__ == "__main__":
    main()
