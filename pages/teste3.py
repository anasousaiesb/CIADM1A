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
        with st.expander("📌 Introdução", expanded=True):
            st.markdown("""
            Este projeto apresenta uma análise climática baseada no dataset do INMET (2020-2025), investigando padrões sazonais, extremos climáticos e tendências futuras. Utilizando séries temporais, mapas de calor e modelos preditivos, buscamos fornecer insights sobre temperatura, precipitação e radiação global no Brasil.

            Os tópicos abordados incluem:
            - **Distribuição da Temperatura Máxima Média**
            - **Comparação de Temperaturas entre Regiões**
            - **Tendências Climáticas**
            - **Impacto Setorial**
            - **Padrões Sazonais Extremos**
            - **Previsões Futuras**

            <div class="highlight-box">
                <p><strong>💡 Dica:</strong> Navegue pelo menu lateral para explorar cada análise detalhadamente.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.subheader("Visão Geral das Análises Disponíveis")
    st.write("Explore os diferentes módulos de análise disponíveis no menu lateral. Abaixo, um resumo dos tópicos:")
    
    # Continuação das seções anteriores...

if __name__ == "__main__":
    main()
