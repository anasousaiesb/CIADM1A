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
            ### **Análise Climática no Brasil com Dados do INMET (2020-2025)**  
            
            A análise climática é fundamental para compreender padrões sazonais e tendências meteorológicas que impactam setores como agricultura, energia e planejamento ambiental. Utilizando dados do INMET, este estudo busca extrair insights valiosos sobre a temperatura, precipitação e radiação global no Brasil.

            **Objetivo da Pesquisa**  
            Explorar a variabilidade climática entre 2020 e 2025, identificando padrões sazonais, extremos climáticos e tendências futuras para auxiliar na tomada de decisões estratégicas.

            **Metodologia**  
            - **Séries temporais** para identificar tendências e variações sazonais.  
            - **Mapas de calor** para visualizar padrões geográficos de temperatura e precipitação.  
            - **Gráficos de dispersão e boxplots** para avaliar extremos climáticos e relações entre variáveis.  
            - **Modelos preditivos** para estimar tendências futuras.  

            **Questões-Chave e Análises**  
            A pesquisa será estruturada em 12 tópicos principais:

            1️⃣ **Qual região do Brasil manteve as temperaturas máximas médias mais elevadas durante a maior parte do ano de 2021? E qual região registrou as temperaturas máximas médias mais baixas, especialmente nos meses de inverno (junho, julho e agosto)?**  
            2️⃣ **Observando a linha da Região Sul (S), em que mês de 2021 ela atingiu sua temperatura máxima média mais baixa? Compare essa temperatura com a temperatura máxima média da Região Nordeste (NE) no mesmo mês.**  
            3️⃣ **Tendências de Curto Prazo: Há tendências de aumento/diminuição de temperatura ou precipitação (2020-2025) em alguma região? O que as explica?**  
            4️⃣ **Diferenças entre Anos: Compare padrões de temperatura e precipitação entre 2020 e 2024 em uma região específica. Isso sugere eventos climáticos ou alta variabilidade?**  
            5️⃣ **Radiação por Estação: Como a radiação global varia entre regiões no verão e inverno? Como isso se relaciona com a geografia de cada região?**  
            6️⃣ **Impacto em Setores: Quais regiões seriam mais favoráveis para agricultura de sequeiro e para energia solar, baseando-se nos dados de temperatura, precipitação e radiação?**  
            7️⃣ **Padrões Sazonais Extremos: Identifique a região com maior amplitude térmica e maior variação de precipitação mensal (2020-2025). Como esses extremos aparecem nos gráficos?**  
            8️⃣ **Previsões Futuras (Insights Preliminares): Que hipóteses sobre o clima futuro das regiões brasileiras podem ser formuladas com base nesses dados de curto prazo (2020-2025)?**  
            9️⃣ **Temperatura Sazonal: Descreva os padrões sazonais de temperatura na Região Sudeste e Nordeste (2020-2025) e identifique meses/anos atípicos.**  
            🔟 **Comparação de Chuva: Compare os regimes de precipitação (volumes, picos/secas) entre as Regiões Norte e Sul (2020-2025) e justifique as diferenças.**  
            1️⃣1️⃣ **Extremos de Radiação: Identifique regiões e meses com maiores/menores valores de Radiação Global (2020-2025) e sua relevância.**  
            1️⃣2️⃣ **Variabilidade Anual: Escolha uma variável e região e analise qual ano (2020-2025) se destaca por valores atipicamente altos/baixos, discutindo as implicações.**  

            **Discussão e Conclusões**  
            Os resultados serão interpretados para fornecer recomendações estratégicas e insights sobre impactos ambientais e setoriais. A confiabilidade dos dados e potenciais melhorias futuras também serão abordadas.

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
