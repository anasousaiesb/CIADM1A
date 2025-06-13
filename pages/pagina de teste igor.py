import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
import numpy as np
from matplotlib.cm import get_cmap

# --- Configurações da Página ---
st.set_page_config(
    layout="wide",
    page_title="Padrões Sazonais de Temperatura (2020-2025) no Brasil 🌡️", # Updated page title
    page_icon="🇧🇷" 
)

# --- CSS para estilização aprimorada do título (Aplicado do design anterior) ---
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fa; /* Fundo suave para o aplicativo */
}
.main-title {
    font-size: 3.5em;
    font-weight: 700;
    color: #2E8B57; /* Um verde mais escuro e atraente */
    text-align: center;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle {
    font-size: 1.8em;
    color: #3CB371; /* Um verde um pouco mais claro */
    text-align: center;
    margin-top: -0.5em;
    margin-bottom: 1.5em;
}
.header-section {
    background-color: #e6f7ee; /* Fundo levemente verde para a seção de cabeçalho */
    padding: 1.5em;
    border-radius: 10px;
    margin-bottom: 2em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# --- Caminho Relativo do Arquivo CSV ---
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# --- Dicionário para Mapear Abrevições das Regiões ---
mapa_regioes = {
    "CO": "Centro-Oeste",
    "NE": "Nordeste",
    "N": "Norte",
    "S": "Sul",
    "SE": "Sudeste"
}

# --- Carregamento e Preparação dos Dados ---
@st.cache_data # Cache os dados para evitar recarregamento em cada interação
def carregar_dados(caminho):
    df = pd.read_csv(caminho)
    df['Regiao'] = df['Regiao'].map(mapa_regioes)
    return df

try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- TÍTULO PRINCIPAL E SUBTÍTULO COM O NOVO DESIGN ---
    st.markdown('<div class="header-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Padrões Sazonais de Temperatura (2020-2025) no Brasil 🌎🌡️📊</h1>', unsafe_allow_html=True) # New Title
    st.markdown("""
    <p class="subtitle">
        Explore e compare as **tendências de temperatura média** em diferentes regiões do país.
        Este aplicativo interativo permite identificar meses e anos com **comportamentos climáticos atípicos**,
        oferecendo uma visão clara das variações sazonais ao longo do período de 2020 a 2025.
    </p>
    """, unsafe_allow_html=True) # New Subtitle
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---") # Separator after the header

    # --- Seleção de Regiões na Barra Lateral ---
    st.sidebar.header("✨ Escolha suas Regiões para Comparação")
    regioes_disponiveis = sorted(df_unificado['Regiao'].dropna().unique())

    # Definir índices padrão para evitar erros se as regiões não existirem
    default_index_sul = regioes_disponiveis.index("Sul") if "Sul" in regioes_disponiveis else 0
    default_index_norte = regioes_disponiveis.index("Norte") if "Norte" in regioes_disponiveis else (1 if len(regioes_disponiveis) > 1 else 0)

    regiao_a = st.sidebar.selectbox("📍 **Região A**", regioes_disponiveis, index=default_index_sul)
    regiao_b = st.sidebar.selectbox("📍 **Região B**", regioes_disponiveis, index=default_index_norte)

    # Verifica se as regiões selecionadas são diferentes
    if regiao_a == regiao_b:
        st.sidebar.warning("⚠️ Por favor, selecione duas regiões **diferentes** para uma análise comparativa eficaz.")
        st.stop() # Interrompe a execução para que o usuário selecione regiões distintas

    coluna_temp = 'Temp_Media'

    # --- Cores para os Anos (Melhorado e Vibrante) ---
    cmap = get_cmap('viridis') # Uma paleta de cores mais vibrante e perceptível
    anos = sorted(df_unificado['Ano'].unique())
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # --- Geração dos Gráficos de Linha ---
    st.subheader(f"📈 Gráficos de Temperatura Média Mensal: **{regiao_a}** vs. **{regiao_b}**")
    st.markdown("Acompanhe a trajetória da temperatura mês a mês, ano a ano.")
    
    # Adjusted figsize for less flattened plots and changed style
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 8), sharey=True) # Increased height
    plt.style.use('ggplot') # Changed style to ggplot

    analise_regioes = {regiao_a: {}, regiao_b: {}}
    meses_atipicos_geral = pd.DataFrame()

    for i, regiao in enumerate([regiao_a, regiao_b]):
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        medias_mensais = df_regiao.groupby(['Ano', 'Mês'])[coluna_temp].mean().reset_index()

        # Cálculos para análise dinâmica de atipicidade
        media_geral = medias_mensais[coluna_temp].mean()
        desvio_padrao = medias_mensais[coluna_temp].std()
        limite_superior = media_geral + 1.5 * desvio_padrao # Limite superior para atípicos
        limite_inferior = media_geral - 1.5 * desvio_padrao # Limite inferior para atípicos
        
        # Armazenar métricas para análise
        analise_regioes[regiao]['media'] = round(media_geral, 1)
        analise_regioes[regiao]['amplitude'] = round(medias_mensais[coluna_temp].max() - medias_mensais[coluna_temp].min(), 1)
        
        # Para evitar erro se idxmax() ou idxmin() retornarem vazio
        if not medias_mensais.empty:
            analise_regioes[regiao]['mes_mais_quente'] = medias_mensais.loc[medias_mensais[coluna_temp].idxmax(), 'Mês']
            analise_regioes[regiao]['mes_mais_frio'] = medias_mensais.loc[medias_mensais[coluna_temp].idxmin(), 'Mês']
        else:
            analise_regioes[regiao]['mes_mais_quente'] = 'N/A'
            analise_regioes[regiao]['mes_mais_frio'] = 'N/A'

        atipicos_regiao = medias_mensais[
            (medias_mensais[coluna_temp] > limite_superior) | (medias_mensais[coluna_temp] < limite_inferior)
        ].copy() # Usar .copy() para evitar SettingWithCopyWarning
        
        atipicos_regiao['Regiao'] = regiao # Adiciona a coluna de região aos atípicos
        analise_regioes[regiao]['num_atipicos'] = len(atipicos_regiao)
        meses_atipicos_geral = pd.concat([meses_atipicos_geral, atipicos_regiao])

        for ano in anos:
            df_ano_regiao = medias_mensais[medias_mensais['Ano'] == ano]
            if not df_ano_regiao.empty:
                axes[i].plot(df_ano_regiao['Mês'], df_ano_regiao[coluna_temp], marker='o', linestyle='-',
                             color=cores_anos[ano], label=f'{ano}', linewidth=2) # Linhas mais grossas

        axes[i].set_title(f"Termômetro de {regiao}", fontsize=18, color='#333333') # Título mais impactante
        axes[i].set_xlabel("Mês do Ano", fontsize=14)
        if i == 0: # Apenas para o primeiro gráfico
            axes[i].set_ylabel("Temperatura Média (°C)", fontsize=14)
        axes[i].set_xticks(range(1, 13))
        axes[i].set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], fontsize=12)
        axes[i].tick_params(axis='both', which='major', labelsize=12)
        axes[i].legend(title="Ano", fontsize=11, title_fontsize=13, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Adiciona a faixa de atipicidade com uma cor suave
        axes[i].axhspan(limite_inferior, limite_superior, color='gold', alpha=0.15, label='Faixa Típica (±1.5 DP)')
        # Adiciona a linha da média geral
        axes[i].axhline(media_geral, color='purple', linestyle='--', linewidth=1.5, label=f'Média Geral ({media_geral:.1f}°C)')
        axes[i].grid(True, linestyle=':', alpha=0.7) # Grid mais suave

    plt.tight_layout(rect=[0, 0, 0.95, 1]) # Ajusta o layout para a legenda não cortar
    st.pyplot(fig)

    # --- Exibir os Meses/Anos Atípicos ---
    st.markdown("---")
    st.subheader("🚨 Meses e Anos com Temperaturas Atípicas Identificadas")
    st.markdown(
        """
        Estas são as ocorrências onde a temperatura média mensal se desviou **significativamente** do padrão
        (fora de $\pm 1.5$ vezes o desvio padrão).
        """
    )
    
    if not meses_atipicos_geral.empty:
        # Renomear colunas para melhor clareza
        meses_atipicos_geral = meses_atipicos_geral.rename(columns={'Mês': 'Mês (Número)', 'Temp_Media': 'Temperatura Média (°C)'})
        st.dataframe(meses_atipicos_geral[['Regiao', 'Ano', 'Mês (Número)', 'Temperatura Média (°C)']].sort_values(by=['Regiao', 'Ano', 'Mês (Número)']), use_container_width=True)
    else:
        st.info("🎉 Nenhuma temperatura atípica foi identificada para as regiões e período selecionados. Que boa notícia!")


    # --- Análise Dinâmica Comparativa ---
    st.markdown("---")
    st.subheader("💡 Análise Comparativa Detalhada entre as Regiões")
    st.markdown(f"Entenda as nuances climáticas e compare as características térmicas de **{regiao_a}** e **{regiao_b}**.")
    
    # Usando colunas para um layout mais organizado
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background-color:#e0f7fa; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
            <h4 style="color:#00796b;">✨ Características de {regiao_a}</h4>
            <ul>
                <li>🌡️ <strong>Temperatura Média Geral:</strong> <span style="color:#e65100; font-weight:bold;">{analise_regioes[regiao_a]['media']}°C</span></li>
                <li>↔️ <strong>Amplitude Térmica Anual:</strong> <span style="color:#c2185b; font-weight:bold;">{analise_regioes[regiao_a]['amplitude']}°C</span></li>
                <li>☀️ <strong>Mês Tipicamente Mais Quente:</strong> Mês {analise_regioes[regiao_a]['mes_mais_quente']}</li>
                <li>❄️ <strong>Mês Tipicamente Mais Frio:</strong> Mês {analise_regioes[regiao_a]['mes_mais_frio']}</li>
                <li>❗ <strong>Eventos Atípicos (meses fora do padrão):</strong> <span style="color:#d32f2f; font-weight:bold;">{analise_regioes[regiao_a]['num_atipicos']}</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color:#fff3e0; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
            <h4 style="color:#ef6c00;">✨ Características de {regiao_b}</h4>
            <ul>
                <li>🌡️ <strong>Temperatura Média Geral:</strong> <span style="color:#00796b; font-weight:bold;">{analise_regioes[regiao_b]['media']}°C</span></li>
                <li>↔️ <strong>Amplitude Térmica Anual:</strong> <span style="color:#880e4f; font-weight:bold;">{analise_regioes[regiao_b]['amplitude']}°C</span></li>
                <li>☀️ <strong>Mês Tipicamente Mais Quente:</strong> Mês {analise_regioes[regiao_b]['mes_mais_quente']}</li>
                <li>❄️ <strong>Mês Tipicamente Mais Frio:</strong> Mês {analise_regioes[regiao_b]['mes_mais_frio']}</li>
                <li>❗ <strong>Eventos Atípicos (meses fora do padrão):</strong> <span style="color:#d32f2f; font-weight:bold;">{analise_regioes[regiao_b]['num_atipicos']}</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔬 Insights e Interpretações dos Dados")
    st.markdown(f"""
    <div style="background-color:#f9fbe7; padding: 25px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
        <p style="font-size:1.1em;">
            A região <strong>{regiao_a if analise_regioes[regiao_a]['amplitude'] > analise_regioes[regiao_b]['amplitude'] else regiao_b}</strong> se destaca por apresentar a **maior variação sazonal** de temperatura. Isso significa que, ao longo do ano, essa região experimenta flutuações mais significativas entre as estações quentes e frias.
        </p>
        <p style="font-size:1.1em;">
            Em termos de calor, a região <strong>{regiao_a if analise_regioes[regiao_a]['media'] > analise_regioes[regiao_b]['media'] else regiao_b}</strong> é, em média, consistentemente **mais quente**, evidenciando um clima predominante com temperaturas elevadas.
        </p>
        <p style="font-size:1.1em;">
            Com <strong>{analise_regioes[regiao_a if analise_regioes[regiao_a]['num_atipicos'] > analise_regioes[regiao_b]['num_atipicos'] else regiao_b]['num_atipicos']}</strong> meses atípicos registrados, a região <strong>{regiao_a if analise_regioes[regiao_a]['num_atipicos'] > analise_regioes[regiao_b]['num_atipicos'] else regiao_b}</strong> demonstra uma **maior propensão a eventos climáticos fora do padrão**, como ondas de calor intensas ou frentes frias incomuns. Isso pode indicar uma maior variabilidade interanual ou a influência de fenômenos climáticos extremos.
        </p>
        <p style="font-size:1.1em;">
            Os gráficos apresentados revelam padrões sazonais notavelmente distintos. Enquanto <strong>{regiao_a}</strong> {f"exibe uma **sazonalidade muito marcada**, com picos e vales de temperatura bem acentuados ao longo do ano" if analise_regioes[regiao_a]['amplitude'] > 5 else "mantém **temperaturas mais estáveis** e menos flutuantes ao longo das estações"}, <strong>{regiao_b}</strong> {f"apresenta **variações mais pronunciadas** entre as estações, indicando um regime térmico mais dinâmico" if analise_regioes[regiao_b]['amplitude'] > 5 else "mostra uma **pequena variação** entre os meses, sugerindo um clima mais homogêneo termicamente"}.
        </p>
        <p style="font-size:1.1em;">
            A detecção desses meses atípicos é vital para compreender os **desvios do clima esperado** e pode estar diretamente ligada a **eventos climáticos extremos**, como secas prolongadas, chuvas torrenciais, ondas de calor sem precedentes ou frentes frias rigorosas, bem como mudanças nos padrões atmosféricos globais.
        </p>
    </div>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"❌ **Erro Crítico:** O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e a existência do arquivo na pasta `medias`.")
    st.info("💡 **Dica:** Certifique-se de que o arquivo `medias_mensais_geo_2020_2025.csv` está localizado corretamente na pasta `medias` dentro do seu projeto.")
except KeyError as e:
    st.error(f"❌ **Erro de Dados:** A coluna esperada '{e}' não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto e se o arquivo está no formato esperado.")
    st.info("💡 **Dica:** O arquivo CSV deve conter colunas como 'Regiao', 'Ano', 'Mês' e 'Temp_Media'.")
except Exception as e:
    st.error(f"💥 **Ops! Ocorreu um erro inesperado:** {e}")
    st.warning("🔄 **Sugestão:** Tente recarregar a página. Se o problema persistir, pode ser um erro nos dados ou no script. Por favor, entre em contato com o suporte técnico se necessário.")

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: small; color: gray;'>
    🌟 Desenvolvido com paixão e dados por [Ana Sophia e Igor Andrade] 🌟
</div>
""", unsafe_allow_html=True)
