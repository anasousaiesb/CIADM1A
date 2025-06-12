import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from matplotlib.cm import get_cmap

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Análise Climática Sazonal do Brasil")

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

# --- Título Principal ---
st.title("🌎 Padrões Sazonais de Temperatura (2020-2025) no Brasil")
st.markdown("Explore e compare as tendências de temperatura média em diferentes regiões do país, identificando meses e anos com comportamentos atípicos.")

# --- Carregamento e Preparação dos Dados ---
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_csv(caminho)
    df['Regiao'] = df['Regiao'].map(mapa_regioes)
    return df

try:
    df_unificado = carregar_dados(caminho_arquivo_unificado)

    # --- Seleção de Regiões na Barra Lateral ---
    st.sidebar.header("Selecione as Regiões para Comparação")
    regioes_disponiveis = sorted(df_unificado['Regiao'].dropna().unique())

    # Definir índices padrão para evitar erros se as regiões não existirem
    default_index_sul = regioes_disponiveis.index("Sul") if "Sul" in regioes_disponiveis else 0
    default_index_norte = regioes_disponiveis.index("Norte") if "Norte" in regioes_disponiveis else (1 if len(regioes_disponiveis) > 1 else 0)

    regiao_a = st.sidebar.selectbox("Região A", regioes_disponiveis, index=default_index_sul)
    regiao_b = st.sidebar.selectbox("Região B", regioes_disponiveis, index=default_index_norte)

    # Verifica se as regiões selecionadas são diferentes
    if regiao_a == regiao_b:
        st.sidebar.warning("Por favor, selecione duas regiões diferentes para comparação.")
        st.stop() # Interrompe a execução para que o usuário selecione regiões distintas

    coluna_temp = 'Temp_Media'

    # --- Cores para os Anos (Melhorado) ---
    cmap = get_cmap('viridis') # Uma paleta de cores mais vibrante
    anos = sorted(df_unificado['Ano'].unique())
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # --- Geração dos Gráficos de Linha ---
    st.subheader(f"📊 Temperaturas Médias Mensais: {regiao_a} vs. {regiao_b}")
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18, 7), sharey=True)
    plt.style.use('seaborn-v0_8-darkgrid') # Estilo mais moderno para os gráficos

    analise_regioes = {regiao_a: {}, regiao_b: {}}
    meses_atipicos_geral = pd.DataFrame()

    for i, regiao in enumerate([regiao_a, regiao_b]):
        df_regiao = df_unificado[df_unificado['Regiao'] == regiao]
        medias_mensais = df_regiao.groupby(['Ano', 'Mês'])[coluna_temp].mean().reset_index()

        # Cálculos para análise dinâmica de atipicidade
        media_geral = medias_mensais[coluna_temp].mean()
        desvio_padrao = medias_mensais[coluna_temp].std()
        limite_superior = media_geral + 1.5 * desvio_padrao
        limite_inferior = media_geral - 1.5 * desvio_padrao
        
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
                             color=cores_anos[ano], label=f'{ano}')

        axes[i].set_title(f"Variação de Temperatura em {regiao}", fontsize=16)
        axes[i].set_xlabel("Mês do Ano", fontsize=12)
        if i == 0: # Apenas para o primeiro gráfico
            axes[i].set_ylabel("Temperatura Média (°C)", fontsize=12)
        axes[i].set_xticks(range(1, 13))
        axes[i].set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
        axes[i].tick_params(axis='both', which='major', labelsize=10)
        axes[i].legend(title="Ano", fontsize=10, title_fontsize=12, bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[i].axhspan(limite_inferior, limite_superior, color='yellow', alpha=0.1, label='Faixa Típica (±1.5 DP)')
        axes[i].axhline(media_geral, color='gray', linestyle='--', linewidth=1, label=f'Média Geral ({media_geral:.1f}°C)')

    plt.tight_layout(rect=[0, 0, 0.95, 1]) # Ajusta o layout para a legenda não cortar
    st.pyplot(fig)

    # --- Exibir os Meses/Anos Atípicos ---
    if not meses_atipicos_geral.empty:
        st.subheader("⚠️ Meses e Anos com Temperaturas Atípicas")
        st.write("Identificados com base em um desvio de $\pm 1.5$ vezes o desvio padrão da temperatura média para cada região.")
        
        # Renomear colunas para melhor clareza
        meses_atipicos_geral = meses_atipicos_geral.rename(columns={'Mês': 'Mês (Número)', 'Temp_Media': 'Temperatura Média (°C)'})
        st.dataframe(meses_atipicos_geral[['Regiao', 'Ano', 'Mês (Número)', 'Temperatura Média (°C)']].sort_values(by=['Regiao', 'Ano', 'Mês (Número)']))
    else:
        st.info("🎉 Nenhuma temperatura atípica foi identificada para as regiões e período selecionados!")


    # --- Análise Dinâmica Comparativa ---
    st.markdown("---") # Separador visual
    st.subheader("💡 Análise Comparativa Detalhada")
    
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3>Comparando {regiao_a} e {regiao_b} (2020-2025)</h3>
        <p>Esta seção oferece um resumo das características térmicas de cada região, facilitando a identificação de padrões e diferenças climáticas.</p>
        
        <div style="display: flex; justify-content: space-around;">
            <div style="background-color:#ffffff; padding: 15px; border-radius: 8px; flex: 1; margin-right: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>{regiao_a}</h4>
                <ul>
                    <li><strong>Temperatura Média Geral:</strong> {analise_regioes[regiao_a]['media']}°C</li>
                    <li><strong>Amplitude Térmica Anual (Máx - Min):</strong> {analise_regioes[regiao_a]['amplitude']}°C</li>
                    <li><strong>Mês Tipicamente Mais Quente:</strong> Mês {analise_regioes[regiao_a]['mes_mais_quente']}</li>
                    <li><strong>Mês Tipicamente Mais Frio:</strong> Mês {analise_regioes[regiao_a]['mes_mais_frio']}</li>
                    <li><strong>Eventos Atípicos (meses fora do padrão):</strong> {analise_regioes[regiao_a]['num_atipicos']}</li>
                </ul>
            </div>
            <div style="background-color:#ffffff; padding: 15px; border-radius: 8px; flex: 1; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>{regiao_b}</h4>
                <ul>
                    <li><strong>Temperatura Média Geral:</strong> {analise_regioes[regiao_b]['media']}°C</li>
                    <li><strong>Amplitude Térmica Anual (Máx - Min):</strong> {analise_regioes[regiao_b]['amplitude']}°C</li>
                    <li><strong>Mês Tipicamente Mais Quente:</strong> Mês {analise_regioes[regiao_b]['mes_mais_quente']}</li>
                    <li><strong>Mês Tipicamente Mais Frio:</strong> Mês {analise_regioes[regiao_b]['mes_mais_frio']}</li>
                    <li><strong>Eventos Atípicos (meses fora do padrão):</strong> {analise_regioes[regiao_b]['num_atipicos']}</li>
                </ul>
            </div>
        </div>
        
        <h4>Conclusões do Comparativo:</h4>
        <ul>
            <li>A região <strong>{regiao_a if analise_regioes[regiao_a]['amplitude'] > analise_regioes[regiao_b]['amplitude'] else regiao_b}</strong> apresenta a maior **amplitude térmica sazonal**, indicando maiores variações de temperatura ao longo do ano.</li>
            <li>Em média, a região <strong>{regiao_a if analise_regioes[regiao_a]['media'] > analise_regioes[regiao_b]['media'] else regiao_b}</strong> é consistentemente mais **quente**.</li>
            <li>A região <strong>{regiao_a if analise_regioes[regiao_a]['num_atipicos'] > analise_regioes[regiao_b]['num_atipicos'] else regiao_b}</strong> registrou **mais meses com temperaturas atípicas**, o que pode sugerir uma maior influência de fenômenos climáticos extremos ou variabilidade interanual.</li>
        </ul>
        <p>
            Os gráficos acima ilustram claramente como <strong>{regiao_a}</strong> {f"possui uma sazonalidade bem definida, com picos e vales acentuados" if analise_regioes[regiao_a]['amplitude'] > 5 else "mantém temperaturas mais estáveis e menos flutuantes ao longo do ano"}, enquanto <strong>{regiao_b}</strong> {f"exibe variações significativas de temperatura entre as estações" if analise_regioes[regiao_b]['amplitude'] > 5 else "demonstra uma variação térmica anual mais contida"}. A identificação de meses atípicos é crucial para entender desvios do clima esperado, que podem estar ligados a eventos como ondas de calor, frentes frias intensas ou anomalias globais.
        </p>
    </div>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"❌ Erro: O arquivo de dados '{caminho_arquivo_unificado}' não foi encontrado. Por favor, verifique o caminho e a existência do arquivo.")
    st.info("Certifique-se de que o arquivo `medias_mensais_geo_2020_2025.csv` está localizado na pasta `medias` dentro do seu projeto.")
except KeyError as e:
    st.error(f"❌ Erro: A coluna '{e}' não foi encontrada no arquivo CSV. Verifique se o nome da coluna está correto.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro inesperado ao gerar os gráficos: {e}")
    st.warning("Se o problema persistir, tente recarregar a página ou verificar a integridade dos dados.")

st.markdown("---")
st.markdown("Desenvolvido com ❤️ por Seu Nome/Equipe")
