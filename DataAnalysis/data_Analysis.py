import pandas as pd
import camelot
import zipfile
import os

# Função para extrair dados do PDF
def extract_table_from_pdf(pdf_path):
    """
    Extrai a primeira tabela de um arquivo PDF usando a biblioteca camelot.

    Args:
        pdf_path (str): O caminho para o arquivo PDF.

    Returns:
        pandas.DataFrame: O DataFrame contendo os dados da tabela.

    Raises:
        FileNotFoundError: Se o arquivo PDF não for encontrado.
        ValueError: Se nenhuma tabela for encontrada no PDF.
        Exception: Se ocorrer um erro durante a leitura do PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"O arquivo PDF não foi encontrado no caminho: {pdf_path}")
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        if not tables:
            raise ValueError("Nenhuma tabela foi encontrada no arquivo PDF.")
        df = tables[0].df
        if df.empty:
            raise ValueError("A tabela extraída está vazia.")
        return df
    except Exception as e:
        raise Exception(f"Ocorreu um erro ao tentar ler o arquivo PDF: {e}")

# Função para substituir as abreviações
def replace_abbreviations(df):
    """
    Substitui abreviações em um DataFrame por suas descrições completas.

    Args:
        df (pandas.DataFrame): O DataFrame a ser modificado.

    Returns:
        pandas.DataFrame: O DataFrame com as abreviações substituídas.

    Raises:
        TypeError: Se o argumento 'df' não for um DataFrame.
        KeyError: Se as colunas a serem manipuladas não existirem no DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("O argumento 'df' deve ser um pandas DataFrame.")
    try:
        if 'OD' in df.columns or df.shape[1] > 0: # Verifica se há colunas ou se o DataFrame não está vazio
            df = df.replace({'OD': 'Ortopedia', 'AMB': 'Ambulatório'})
        return df
    except KeyError as e:
        raise KeyError(f"Erro ao substituir abreviações: a coluna '{e}' não foi encontrada no DataFrame.")
    except Exception as e:
        raise Exception(f"Ocorreu um erro ao substituir abreviações: {e}")

# Função para salvar os dados em CSV
def save_to_csv(df, file_name):
    """
    Salva um DataFrame em um arquivo CSV.

    Args:
        df (pandas.DataFrame): O DataFrame a ser salvo.
        file_name (str): O nome do arquivo CSV a ser criado.

    Raises:
        TypeError: Se o argumento 'df' não for um DataFrame.
        IOError: Se ocorrer um erro ao escrever no arquivo CSV.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("O argumento 'df' deve ser um pandas DataFrame.")
    try:
        df.to_csv(file_name, index=False)
    except IOError as e:
        raise IOError(f"Erro ao salvar o arquivo CSV '{file_name}': {e}")
    except Exception as e:
        raise Exception(f"Ocorreu um erro ao salvar o arquivo CSV: {e}")

# Função para compactar o CSV em um arquivo ZIP
def compress_to_zip(csv_file, zip_file):
    """
    Compacta um arquivo CSV em um arquivo ZIP.

    Args:
        csv_file (str): O caminho para o arquivo CSV a ser compactado.
        zip_file (str): O nome do arquivo ZIP a ser criado.

    Raises:
        FileNotFoundError: Se o arquivo CSV não for encontrado.
        IOError: Se ocorrer um erro ao escrever no arquivo ZIP.
        Exception: Se ocorrer um erro durante a compactação.
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"O arquivo CSV não foi encontrado no caminho: {csv_file}")
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_file, os.path.basename(csv_file))
    except IOError as e:
        raise IOError(f"Erro ao criar o arquivo ZIP '{zip_file}': {e}")
    except Exception as e:
        raise Exception(f"Ocorreu um erro ao compactar o arquivo: {e}")

# Função principal
def main():
    """
    Função principal para executar a análise de dados do PDF.
    """
    pdf_path = 'WebScrapping/pdf_files/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf'
    csv_file = 'Tabela.csv'
    zip_file = 'Teste_{Pedro}.zip'

    try:
        print(f"Iniciando processamento do arquivo: {pdf_path}")

        # 1. Extrair os dados da tabela
        print("Extraindo tabela do PDF...")
        df = extract_table_from_pdf(pdf_path)
        print("Tabela extraída com sucesso.")
        print(df.head())

        # 2. Substituir abreviações
        print("Substituindo abreviações...")
        df = replace_abbreviations(df)
        print("Abreviações substituídas com sucesso.")
        print(df.head())

        # 3. Salvar em CSV
        print(f"Salvando dados em '{csv_file}'...")
        save_to_csv(df, csv_file)
        print(f"Dados salvos com sucesso em '{csv_file}'.")

        # 4. Compactar o CSV em ZIP
        print(f"Compactando '{csv_file}' em '{zip_file}'...")
        compress_to_zip(csv_file, zip_file)
        print(f"Arquivo CSV compactado criado com sucesso: {zip_file}")

        print("Processamento concluído com sucesso!")

    except FileNotFoundError as e:
        print(f"Erro: {e}")
    except ValueError as e:
        print(f"Erro: {e}")
    except TypeError as e:
        print(f"Erro: {e}")
    except KeyError as e:
        print(f"Erro: {e}")
    except IOError as e:
        print(f"Erro de I/O: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        # Limpeza (opcional, mas pode ser útil em alguns cenários)
        if os.path.exists(csv_file):
            print(f"Limpando arquivo temporário: {csv_file}")
            os.remove(csv_file)

if __name__ == '__main__':
    main()