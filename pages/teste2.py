import streamlit as st

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Análises de Dados - CIADM1A", # Título da aba do navegador alterado
        page_icon="📊",  # Ícone da aba do navegador alterado para algo mais genérico
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
        height: 150px; /* Altura fixa para melhor alinhamento dos cards */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .custom-card h4 {
        font-size: 1.1em; /* Ajuste no tamanho da fonte do título do card */
    }
    .custom-card p {
        font-size: 0.9em; /* Ajuste no tamanho da fonte da descrição do card */
        color:#7f8c8d;
    }
    .highlight-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho
    st.title("Projeto de Análise de Dados") # Título principal alterado
    st.subheader("CIADM1A-CIA001-20251")
    
    # Divisor
    st.write("---")

    # Seção de informações da equipe
    col1, col2 = st.columns([1, 2]) # Mantendo a proporção, pode ajustar se necessário

    with col1:
        # Professor
        st.subheader("Professor:")
        st.markdown("""
        <div class="custom-card" style="height: auto;"> Alexandre Vaz Roriz
        </div>
        """, unsafe_allow_html=True)
        
        # Alunos
        st.subheader("Alunos:")
        st.markdown("""
        <div class="custom-card" style="height: auto;"> Ana Sophia<br>
            Igor Andrade
        </div>
        """, unsafe_allow_html=True)

    # Introdução
    with st.expander("📌 Introdução ao Projeto", expanded=True): # Introdução pode vir expandida por padrão
        st.markdown("""
        Este projeto apresenta uma coleção de análises de dados desenvolvidas como parte da disciplina de Introdução à Ciência de Dados.
        Exploramos diferentes conjuntos de dados e técnicas para extrair informações e apresentar visualizações interativas.
        
        O objetivo é aplicar os conceitos aprendidos para analisar, interpretar e comunicar resultados a partir de dados diversos.

        ### **Entre os tópicos explorados, destacamos:**
        Navegue pelas seções abaixo para visualizar cada uma das análises desenvolvidas. Cada card representa um estudo ou ferramenta específica criada para investigar diferentes aspectos dos dados.

        <div class="highlight-box">
            <p><strong>💡 Dica:</strong> Clique nos cards abaixo ou utilize o menu lateral (se configurado em páginas separadas) para acessar cada tópico da análise.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Divisor
    st.write("---")
    
    # Seção de navegação
    st.subheader("Explore Nossas Análises")
    st.write("Selecione um card abaixo para visualizar a análise correspondente:")
    
    sections = [
        ("☀️", "Análise de Radiação Global em 2020", "Detalhes da radiação global no ano de 2020."),
        ("📅", "Análise Anual", "Estudos e comparações baseados em dados anuais."), # "ano" adaptado
        ("🗺️", "Facetado por Região e Variável", "Dados segmentados por região e múltiplas variáveis."),
        ("📈", "Médias Mensais por Estado", "Consulta de médias mensais com filtro por estado."), # "selecionável" implícito na descrição
        ("📊", "Médias Mensais Regionais (2020-2025)", "Médias por região para o período 2020-2025."),
        ("📄", "Página 2", "Conteúdo ou análise adicional."), # "page2"
        ("🧪", "Testes", "Demonstrações e testes de funcionalidades.") # "teste"
    ]
    
    # Exibir os cards em até 4 colunas por linha
    num_cols = 4 
    for i in range(0, len(sections), num_cols):
        cols = st.columns(num_cols)
        for j, (icon, title, desc) in enumerate(sections[i:i+num_cols]):
            with cols[j]:
                st.markdown(f"""
                <div class="custom-card">
                    <div>
                        <h4>{icon} {title}</h4>
                        <p>{desc}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Rodapé
    st.write("---")
    st.caption("Trabalho desenvolvido para a disciplina de Introdução à Ciência de Dados - 2025/1")
    # Removida a menção específica ao dataset do IBGE, pois os tópicos são outros
    st.caption("Fontes de dados variadas, conforme cada análise.") 

if __name__ == "__main__":
    main()
