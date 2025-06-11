import os
import pandas as pd
from pathlib import Path

# Definindo o caminho relativo
caminho_arquivo_unificado = os.path.join("medias", "medias_mensais_geo_2020_2025.csv")

# Solução 1: Verificação básica
if os.path.exists(caminho_arquivo_unificado):
    print(f"Arquivo encontrado em: {os.path.abspath(caminho_arquivo_unificado)}")
    df = pd.read_csv(caminho_arquivo_unificado)
else:
    print("Arquivo não encontrado. Verificando alternativas...")
    
    # Solução 2: Tentar caminhos alternativos
    caminhos_alternativos = [
        os.path.join("..", "medias", "medias_mensais_geo_2020_2025.csv"),  # Um nível acima
        os.path.join(Path(__file__).parent, "medias", "medias_mensais_geo_2020_2025.csv"),  # Relativo ao script
        os.path.join(Path(__file__).parent.parent, "medias", "medias_mensais_geo_2020_2025.csv")  # Dois níveis acima
    ]
    
    for caminho in caminhos_alternativos:
        if os.path.exists(caminho):
            print(f"Arquivo encontrado em: {os.path.abspath(caminho)}")
            df = pd.read_csv(caminho)
            break
    else:
        raise FileNotFoundError(
            f"Não foi possível encontrar o arquivo 'medias_mensais_geo_2020_2025.csv' em:\n"
            f"- {os.path.abspath('medias')}\n"
            f"- Ou em qualquer dos caminhos alternativos testados"
        )

# Se chegou aqui, o arquivo foi carregado com sucesso
print("Dados carregados com sucesso!")
print(f"Total de linhas: {len(df)}")
print(f"Colunas disponíveis: {list(df.columns)}")
