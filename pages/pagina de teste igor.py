import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# --- CONFIGURAÇÕES ---
CAMINHO_CSV = "dados_climaticos.csv"  # Arquivo de dados
REGIAO_DESEJADA = "Sudeste"           # Região a ser analisada

# --- LEITURA E PRÉ-PROCESSAMENTO ---
df = pd.read_csv(CAMINHO_CSV)

# Padronização dos nomes das colunas
col_max = 'TEMPERATURA MAXIMA (°C)'
col_min = 'TEMPERATURA MINIMA (°C)'
col_mes = 'MÊS'
col_ano = 'ANO'
col_regiao = 'REGIAO'

# Cálculo da amplitude térmica com tratamento de outliers
df['Amplitude_Termica'] = df[col_max] - df[col_min]

# Filtro da região e remoção de valores nulos
df_regiao = df[df[col_regiao] == REGIAO_DESEJADA].copy()
df_regiao = df_regiao.dropna(subset=['Amplitude_Termica', col_mes, col_ano])

# --- ANÁLISE ESTATÍSTICA ---
# Estatísticas descritivas por mês
estatisticas_mensais = df_regiao.groupby(col_mes)['Amplitude_Termica'].describe()
print("\nEstatísticas Mensais da Amplitude Térmica:")
print(estatisticas_mensais)

# Teste de tendência temporal (Mann-Kendall)
anos_unicos = sorted(df_regiao[col_ano].unique())
if len(anos_unicos) >= 4:  # Requer pelo menos 4 anos para análise de tendência
    media_anual = df_regiao.groupby(col_ano)['Amplitude_Termica'].mean()
    tau, p_value = stats.kendalltau(media_anual.index, media_anual.values)
    print(f"\nTendência temporal (p-value): {p_value:.4f}")
    if p_value < 0.05:
        print("Tendência estatisticamente significativa detectada!")
    else:
        print("Nenhuma tendência significativa detectada.")

# --- VISUALIZAÇÕES MELHORADAS ---
plt.style.use('seaborn')

# Gráfico 1: Boxplot mensal com distribuição
plt.figure(figsize=(14, 7))
sns.boxplot(x=col_mes, y='Amplitude_Termica', data=df_regiao, palette="coolwarm", 
            showmeans=True, meanprops={"marker":"o","markerfacecolor":"white"})
plt.title(f"Distribuição Mensal da Amplitude Térmica Diária\nRegião: {REGIAO_DESEJADA}", pad=20)
plt.xlabel("Mês", labelpad=10)
plt.ylabel("Amplitude Térmica (°C)", labelpad=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
sns.despine()
plt.tight_layout()
plt.show()

# Gráfico 2: Evolução temporal com intervalo de confiança
plt.figure(figsize=(14, 6))
sns.lineplot(x=col_ano, y='Amplitude_Termica', data=df_regiao, 
             ci=95, estimator='mean', color='darkred', marker='o')
plt.title(f"Evolução Anual da Média de Amplitude Térmica com IC 95%\nRegião: {REGIAO_DESEJADA}", pad=20)
plt.xlabel("Ano", labelpad=10)
plt.ylabel("Média Amplitude Térmica (°C)", labelpad=10)
plt.grid(True, linestyle='--', alpha=0.5)
sns.despine()
plt.tight_layout()
plt.show()

# Gráfico 3: Heatmap mensal-anual
pivot_table = df_regiao.pivot_table(values='Amplitude_Termica', 
                                   index=col_ano, columns=col_mes, 
                                   aggfunc='median')
plt.figure(figsize=(12, 8))
sns.heatmap(pivot_table, cmap="YlOrRd", annot=True, fmt=".1f", 
            linewidths=.5, cbar_kws={'label': 'Amplitude Térmica (°C)'})
plt.title(f"Variação Mensal-Anual da Amplitude Térmica\nRegião: {REGIAO_DESEJADA}", pad=20)
plt.xlabel("Mês", labelpad=10)
plt.ylabel("Ano", labelpad=10)
plt.tight_layout()
plt.show()

# --- IDENTIFICAÇÃO DE PADRÕES ---
# Mês com maior variabilidade
coef_var_mensal = df_regiao.groupby(col_mes)['Amplitude_Termica'].std() / df_regiao.groupby(col_mes)['Amplitude_Termica'].mean()
mes_mais_variavel = coef_var_mensal.idxmax()

# Ano mais atípico (teste Z-score)
z_scores = stats.zscore(media_anual)
ano_atipico = media_anual.index[abs(z_scores).argmax()]

print("\nPrincipais Achados:")
print(f"- Mês com maior variabilidade: {mes_mais_variavel} (CV: {coef_var_mensal.max():.2f})")
print(f"- Ano mais atípico: {ano_atipico} (Z-score: {z_scores.max():.2f})")
print(f"- Amplitude média anual: {media_anual.mean():.1f}°C (±{media_anual.std():.1f}°C)")

# --- RECOMENDAÇÕES BASEADAS NOS DADOS ---
print("\nRecomendações:")
print("1. Analisar as causas da maior variabilidade no mês", mes_mais_variavel)
print("2. Investigar fatores climáticos específicos do ano", ano_atipico)
print("3. Monitorar tendência de aumento/redução da amplitude térmica")
