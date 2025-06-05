import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class AnaliseClimatica:
    def __init__(self, dados):
        """
        Inicializa a classe com os dados climáticos
        
        Args:
            dados (DataFrame): DataFrame contendo os dados climáticos
        """
        self.dados = dados
        
    def analise_radiacao_global_2020(self):
        """
        1. Análise de Radiação Global em 2020
        Gera gráficos e estatísticas da radiação global no ano de 2020
        """
        dados_2020 = self.dados[self.dados['ano'] == 2020]
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=dados_2020, x='mes', y='radiacao_global', hue='regiao')
        plt.title('1. Análise de Radiação Global em 2020')
        plt.xlabel('Mês')
        plt.ylabel('Radiação Global (kWh/m²)')
        plt.grid(True)
        plt.show()
        
    def qualidade_dados_correlacoes(self):
        """
        2. Qualidade dos Dados e Correlações Climáticas
        Analisa a qualidade dos dados e calcula correlações entre variáveis climáticas
        """
        print("2. Qualidade dos Dados:")
        print(self.dados.isnull().sum())
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(self.dados.corr(), annot=True, cmap='coolwarm')
        plt.title('Correlações Climáticas')
        plt.show()
        
    def padroes_sazonais_extremos(self):
        """
        3. Padrões Sazonais Extremos
        Identifica padrões sazonais extremos nos dados climáticos
        """
        extremos = self.dados.groupby('estacao').agg({
            'temperatura': ['max', 'min'],
            'radiacao_global': 'max'
        })
        print("3. Padrões Sazonais Extremos:")
        print(extremos)
        
    def radiacao_por_estacao(self):
        """
        4. Radiação Global por Estação
        Compara os níveis de radiação global por estação do ano
        """
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.dados, x='estacao', y='radiacao_global')
        plt.title('4. Radiação Global por Estação')
        plt.xlabel('Estação do Ano')
        plt.ylabel('Radiação Global (kWh/m²)')
        plt.show()
        
    def comparacao_chuva_regioes(self):
        """
        5. Comparação de Chuva entre Regiões Norte e Sul
        Compara os padrões de chuva entre as regiões norte e sul
        """
        norte = self.dados[self.dados['regiao'] == 'Norte']
        sul = self.dados[self.dados['regiao'] == 'Sul']
        
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        sns.histplot(norte['precipitacao'], kde=True)
        plt.title('Precipitação - Região Norte')
        
        plt.subplot(1, 2, 2)
        sns.histplot(sul['precipitacao'], kde=True)
        plt.title('Precipitação - Região Sul')
        
        plt.suptitle('5. Comparação de Chuva entre Regiões Norte e Sul')
        plt.tight_layout()
        plt.show()
        
    def temperatura_sazonal(self):
        """
        6. Temperatura Sazonal
        Analisa a variação sazonal da temperatura
        """
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=self.dados, x='mes', y='temperatura', hue='estacao', 
                    style='estacao', markers=True)
        plt.title('6. Temperatura Sazonal')
        plt.xlabel('Mês')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        plt.show()
        
    def extremos_radiacao(self):
        """
        7. Extremos de Radiação
        Identifica e analisa os extremos de radiação global
        """
        max_rad = self.dados.nlargest(5, 'radiacao_global')
        min_rad = self.dados.nsmallest(5, 'radiacao_global')
        
        print("7. Extremos de Radiação:")
        print("Maiores valores de radiação:")
        print(max_rad[['data', 'regiao', 'radiacao_global']])
        print("\nMenores valores de radiação:")
        print(min_rad[['data', 'regiao', 'radiacao_global']])

# Exemplo de uso
if __name__ == "__main__":
    # Carregar dados (exemplo)
    dados = pd.read_csv('dados_climaticos.csv')
    
    # Converter data se necessário
    dados['data'] = pd.to_datetime(dados['data'])
    dados['ano'] = dados['data'].dt.year
    dados['mes'] = dados['data'].dt.month
    dados['estacao'] = dados['data'].dt.month.apply(lambda x: 
        'Verão' if x in [12, 1, 2] else
        'Outono' if x in [3, 4, 5] else
        'Inverno' if x in [6, 7, 8] else 'Primavera')
    
    # Criar e executar análises
    analise = AnaliseClimatica(dados)
    analise.analise_radiacao_global_2020()
    analise.qualidade_dados_correlacoes()
    analise.padroes_sazonais_extremos()
    analise.radiacao_por_estacao()
    analise.comparacao_chuva_regioes()
    analise.temperatura_sazonal()
    analise.extremos_radiacao()
