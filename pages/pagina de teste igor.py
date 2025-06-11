import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURAÇÕES ---
CAMINHO_CSV = "dados_climaticos.csv"  # <--- Altere para o seu arquivo
REGIAO_DESEJADA = "Sudeste"           # <--- Altere para a região desejada (ou use input() se quiser interatividade)

# --- LEITURA E PRÉ-PROCESSAMENTO ---
df = pd.read_csv(CAMINHO_CSV)

# Ajuste os nomes das colunas conforme o seu arquivo
col_max = 'TEMPERATURA MAXIMA (°C)'
col_min = 'TEMPERATURA MINIMA (°C)'
col_mes = 'MÊS'
col_ano = 'ANO'
col_regiao = 'REGIAO'

# Calcula a amplitude térmica diária
df['Amplitude_Termica_Diaria'] = df[col_max] - df[col_min]

# Filtra a região desejada
df_regiao = df[df[col_regiao] == REGIAO_DESEJADA].copy()

# Remove valores faltantes
df_regiao = df_regiao.dropna(subset=['Amplitude_Termica_Diaria', col_mes, col_ano])

# --- GRÁFICO 1: Boxplot da amplitude térmica por mês ---
plt.figure(figsize=(12,6))
sns.boxplot(x=col_mes, y='Amplitude_Termica_Diaria', data=df_regiao, palette="coolwarm")
plt.title(f"Distribuição da Amplitude Térmica Diária por Mês\nRegião: {REGIAO_DESEJADA}")
plt.xlabel("Mês")
plt.ylabel("Amplitude Térmica Diária (°C)")
plt.show()

# --- GRÁFICO 2: Linha da média anual da amplitude térmica ---
media_anual = df_regiao.groupby(col_ano)['Amplitude_Termica_Diaria'].mean()
plt.figure(figsize=(8,5))
plt.plot(media_anual.index, media_anual.values, marker='o', color='purple')
plt.title(f"Média Anual da Amplitude Térmica Diária\nRegião: {REGIAO_DESEJADA}")
plt.xlabel("Ano")
plt.ylabel("Média Amplitude Térmica (°C)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# --- ANÁLISE DE VARIAÇÕES MAIS ACENTUADAS ---
# Mês com maior mediana
median_amplitude_by_month = df_regiao.groupby(col_mes)['Amplitude_Termica_Diaria'].median()
mes_max = median_amplitude_by_month.idxmax()
# Ano com maior média
mean_amplitude_by_year = df_regiao.groupby(col_ano)['Amplitude_Termica_Diaria'].mean()
ano_max = mean_amplitude_by_year.idxmax()

print(f"O mês com maior mediana de amplitude térmica é: {mes_max}")
print(f"O ano com maior média de amplitude térmica é: {ano_max}")
