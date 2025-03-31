import pandas as pd
import os

def calcular_relevancia(df):
    """
    Calcula a pontuação de relevância das operadoras com base em critérios pré-definidos.
    """
    # Critério 1: Cobertura Geográfica
    cobertura_weights = {'Nacional': 3, 'Regional': 2, 'Estadual': 1}
    df['relevance'] = df['Regiao_de_Comercializacao'].map(cobertura_weights).fillna(1)
    
    # Critério 2: Tempo de Mercado (em anos)
    df['Data_Registro_ANS'] = pd.to_datetime(df['Data_Registro_ANS'], errors='coerce')
    df['anos_mercado'] = (pd.to_datetime('today') - df['Data_Registro_ANS']).dt.days / 365
    df['relevance'] += df['anos_mercado'].rank(pct=True) * 2  # Normalizado entre 0-2
    
    # Critério 3: Modalidade
    modalidade_rank = {'Autogestão': 3, 'Cooperativa Médica': 2, 'Odontológica': 1}
    df['relevance'] += df['Modalidade'].map(modalidade_rank).fillna(1)
    
    # Critério 4: Presença Digital
    df['relevance'] += df['Endereco_eletronico'].notna().astype(int)
    
    # Critério 5: Dados de Contato
    df['relevance'] += (
        df['Telefone'].notna().astype(int) + 
        df['Fax'].notna().astype(int)
    )
    
    return df.sort_values('relevance', ascending=False)

def load_operadoras_data():
    # Caminho absoluto para o arquivo CSV
    csv_path = "Relatorio_cadop.csv"
    
    print(f"Tentando carregar arquivo em: {csv_path}")  # Para debug
    
    try:
        # Carrega os dados
        print("Dados carregados")  # Para debug
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        
        # Aplica cálculo de relevância
        df = calcular_relevancia(df)
        
        return df.fillna('')  # Substitui NaN por strings vazias
    
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame() 