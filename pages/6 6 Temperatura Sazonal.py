import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Caminho relativo ao arquivo CSV dentro do projeto
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_temp_media_completo.csv")

st.title("Análise Comparativa de Temperaturas Médias Mensais (2020-2025)")
st.subheader("Regiões Sudeste e Nordeste")

try:
    # Ler o arquivo unificado com codificação específica (muitas vezes resolve problemas com acentos)
    # 'latin1' é frequentemente bom para arquivos com caracteres especiais em português
    df_unificado = pd.read_csv(caminho_arquivo_unificado, encoding='latin1')
    
    # --- DEBUG: Imprimir colunas para verificar nomes exatos que o Pandas leu ---
    st.write("---")
    st.write("Colunas encontradas no CSV (para depuração):", df_unificado.columns.tolist())
    st.write("---")
    # --- FIM DEBUG ---

    # --- Verificações e Normalizações de Colunas Essenciais ---

    # Normaliza a coluna 'Regiao' (remove espaços extras e padroniza para maiúsculas)
    if 'Regiao' in df_unificado.columns:
        df_unificado['Regiao'] = df_unificado['Regiao'].astype(str).str.strip().str.upper() # Adicionado .astype(str) para robustez
    else:
        st.error("Erro: A coluna 'Regiao' não foi encontrada no arquivo CSV. Verifique o cabeçalho do seu arquivo.")
        st.stop()
    
    # Verifica se 'Mês' existe (conforme a amostra)
    if 'Mês' not in df_unificado.columns:
        st.error("Erro: A coluna 'Mês' não foi encontrada no arquivo CSV. Verifique o cabeçalho do seu arquivo. (Esperado 'Mês' sem acento).")
        st.stop()

    # Verifica se 'Temp_Media' existe (conforme a amostra)
    if 'Temp_Media' not in df_unificado.columns:
        st.error("Erro: A coluna 'Temp_Media' não foi encontrada no arquivo CSV. Verifique o cabeçalho do seu arquivo.")
        st.stop()
    
    # Verifica se 'Ano' existe
    if 'Ano' not in df_unificado.columns:
        st.error("Erro: A coluna 'Ano' não foi encontrada no arquivo CSV. Verifique o cabeçalho do seu arquivo.")
        st.stop()

    # --- Fim das Verificações e Normalizações ---


    # Lista de anos e meses únicos
    # Certifica que 'Mês' é numérico para sorting
    df_unificado['Mês'] = pd.to_numeric(df_unificado['Mês'], errors='coerce')
    df_unificado.dropna(subset=['Mês'], inplace=True) # Remove linhas com Mês inválido
    meses = sorted(df_unificado['Mês'].unique()) 
    anos = sorted(df_unificado['Ano'].unique())


    # Variável a ser analisada (fixa para a pergunta específica: Temperatura Média)
    nome_var = 'Temperatura Média (°C)'
    coluna_var = 'Temp_Media' # Esta coluna agora existe diretamente no CSV

    # Cores para os anos
    from matplotlib.cm import get_cmap
    cmap = get_cmap('viridis')
    cores_anos = {ano: cmap(i / len(anos)) for i, ano in enumerate(anos)}

    # --- Gráfico para a Região Sudeste ---
    st.markdown("---")
    st.subheader(f"{nome_var} na Região Sudeste (2020-2025)")
    
    # A filtragem agora usa 'SUDESTE' (tudo maiúsculo e sem espaços)
    df_sudeste = df_unificado[df_unificado['Regiao'] == 'SUDESTE'] 
    
    if df_sudeste.empty:
        st.warning("Dados para a Região Sudeste não encontrados no arquivo CSV. Verifique o nome EXATO da região na coluna 'Regiao' após a normalização (e.g., 'SUDESTE').")
    else:
        fig_sudeste, ax_sudeste = plt.subplots(figsize=(10, 6))
        # Agrupa por 'Mês' e usa 'coluna_var' ('Temp_Media')
        df_ano_sudeste_grouped = df_sudeste.groupby(['Ano', 'Mês'])[coluna_var].mean().unstack(level=0)
        
        for ano in anos:
            if ano in df_ano_sudeste_grouped.columns:
                ax_sudeste.plot(meses, df_ano_sudeste_grouped[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        
        ax_sudeste.set_title(f'Média Mensal de {nome_var} - Sudeste (2020-2025)')
        ax_sudeste.set_xlabel('Mês')
        ax_sudeste.set_ylabel(nome_var)
        ax_sudeste.set_xticks(meses)
        ax_sudeste.grid(True)
        ax_sudeste.legend(title='Ano')
        plt.tight_layout()
        st.pyplot(fig_sudeste)

    # --- Gráfico para a Região Nordeste ---
    st.markdown("---")
    st.subheader(f"{nome_var} na Região Nordeste (2020-2025)")
    
    # A filtragem agora usa 'NORDESTE' (tudo maiúsculo e sem espaços)
    df_nordeste = df_unificado[df_unificado['Regiao'] == 'NORDESTE']
    
    if df_nordeste.empty:
        st.warning("Dados para a Região Nordeste não encontrados no arquivo CSV. Verifique o nome EXATO da região na coluna 'Regiao' após a normalização (e.g., 'NORDESTE').")
    else:
        fig_nordeste, ax_nordeste = plt.subplots(figsize=(10, 6))
        # Agrupa por 'Mês' e usa 'coluna_var' ('Temp_Media')
        df_ano_nordeste_grouped = df_nordeste.groupby(['Ano', 'Mês'])[coluna_var].mean().unstack(level=0)

        for ano in anos:
            if ano in df_ano_nordeste_grouped.columns:
                ax_nordeste.plot(meses, df_ano_nordeste_grouped[ano].reindex(meses).values, marker='o', linestyle='-', color=cores_anos[ano], label=str(ano))
        
        ax_nordeste.set_title(f'Média Mensal de {nome_var} - Nordeste (2020-2025)')
        ax_nordeste.set_xlabel('Mês')
        ax_nordeste.set_ylabel(nome_var)
        ax_nordeste.set_xticks(meses)
        ax_nordeste.grid(True)
        ax_nordeste.legend(title='Ano')
        plt.tight_layout()
        st.pyplot(fig_nordeste)

    # --- Seção de Comparação e Análise ---
    st.markdown("---")
    st.subheader("Comparação dos Padrões Sazonais de Temperatura (2020-2025)")
    st.write("""
    Ao observar os gráficos de **Temperatura Média (°C)** das regiões Sudeste e Nordeste, podemos identificar padrões sazonais distintos e possíveis anomalias no período de 2020 a 2025.
    """)

    st.markdown("#### **Região Sudeste: Estações Bem Definidas**")
    st.write("""
    A Região Sudeste (SP, RJ, MG, ES) exibe um **padrão sazonal de temperatura bem definido**, com as quatro estações nítidas nos gráficos:
    * **Verão (Dezembro a Março):** Note os **picos de temperatura** mais altos. Este é o período mais quente e úmido.
    * **Outono (Abril a Junho):** As temperaturas começam a **declinar gradualmente**, mostrando uma transição para o frio.
    * **Inverno (Julho a Setembro):** Apresenta os **vales de temperatura**, sendo a estação mais fria e geralmente mais seca. Pode haver a influência de massas de ar polar, causando quedas acentuadas.
    * **Primavera (Outubro a Novembro):** As temperaturas iniciam uma **ascensão gradual**, preparando para o verão.

    **Identificando Meses/Anos Atípicos no Sudeste (2020-2025):**
    Para encontrar anomalias, observe as linhas individuais de cada ano. Se a linha de um ano estiver **significativamente acima** (mais quente) ou **abaixo** (mais fria) da média dos outros anos para um determinado mês, isso indica um evento atípico. Por exemplo, **Maio de 2025** pode mostrar temperaturas atipicamente baixas (linha de 2025 para maio **visivelmente abaixo** das outras), refletindo fortes frentes frias. "Veranicos" podem causar picos de calor em meses que deveriam ser mais amenos.
    """)

    st.markdown("#### **Região Nordeste: Temperaturas Elevadas e Estáveis**")
    st.write("""
    A Região Nordeste, devido à sua localização próxima ao Equador, demonstra um **padrão de temperatura mais elevado e estável ao longo do ano**, com menor variação sazonal do que o Sudeste. As "estações" são mais influenciadas pelo regime de chuvas do que pela temperatura.
    * **Temperaturas Altas Constantes:** As linhas no gráfico permanecerão em **patamares consistentemente altos** na maioria dos meses, com pouca amplitude térmica anual. O gráfico parecerá mais "achatado" em comparação ao do Sudeste.
    * **Picos de Calor:** Embora a variação seja menor, os meses de **setembro a dezembro** (primavera/início do verão) tendem a apresentar os picos ligeiramente mais altos, especialmente nas áreas mais secas do interior.

    **Identificando Meses/Anos Atípicos no Nordeste (2020-2025):**
    Busque por desvios em relação ao padrão de alta estabilidade:
    * **Ondas de Calor:** Picos acentuados de temperatura (linhas **significativamente acima** das demais para um período) indicam ondas de calor. O **Verão de 2025**, por exemplo, foi previsto com temperaturas acima da média em algumas áreas, o que pode se refletir em picos na linha de 2025.
    * **Impacto da La Niña:** Em anos de La Niña (como parte de 2025), pode-se observar períodos ligeiramente mais amenos (linhas um pouco mais baixas) devido ao aumento da nebulosidade e chuvas.
    """)
    st.write("""
    **Em Resumo:**
    Observe a **amplitude vertical** dos gráficos: o do Sudeste mostrará uma variação anual muito maior (picos e vales acentuados), enquanto o do Nordeste exibirá um perfil mais "plano" e elevado. Os meses/anos atípicos se destacam como **"saltos" ou "mergulhos" inesperados** nas linhas individuais dos anos, desviando-se da tendência geral.
    """)

except FileNotFoundError:
    st.error(f"Erro: O arquivo '{caminho_arquivo_unificado}' não foi encontrado. Certifique-se de que ele está no diretório 'medias' dentro do projeto.")
except KeyError as e:
    st.error(f"Ocorreu um erro relacionado a uma coluna ausente ou nomeada incorretamente. Verifique a mensagem: '{e}'. Isso geralmente indica que um nome de coluna no seu código não corresponde ao nome exato no seu CSV.")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao gerar os gráficos: {e}")
