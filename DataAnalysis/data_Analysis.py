import pandas as pd
import tabula
import zipfile
import os

# Função para extrair dados do PDF usando tabula-py
def extract_table_from_pdf_tabula(pdf_path):
    """
    Extrai todas as tabelas de um arquivo PDF usando a biblioteca tabula-py.

    Args:
        pdf_path (str): O caminho para o arquivo PDF.

    Returns:
        list: Uma lista de pandas.DataFrame, onde cada DataFrame representa uma tabela.

    Raises:
        FileNotFoundError: Se o arquivo PDF não for encontrado.
        Exception: Se ocorrer um erro durante a leitura do PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"O arquivo PDF não foi encontrado no caminho: {pdf_path}")
    try:
        try:
            tables = tabula.read_pdf(pdf_path, pages='all', stream=True, guess=False)
            if not tables:
                tables = tabula.read_pdf(pdf_path, pages='all', stream=False, guess=False)
        except ImportError:
            print("Aviso: Não foi possível importar jpype. A extração pode ser mais lenta.")
            tables = tabula.read_pdf(pdf_path, pages='all', stream=True, guess=False)
            if not tables:
                tables = tabula.read_pdf(pdf_path, pages='all', stream=False, guess=False)

        return tables if tables else []

    except Exception as e:
        raise Exception(f"Ocorreu um erro ao tentar ler o arquivo PDF com tabula-py: {e}")

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
        if 'OD' in df.columns or df.shape[1] > 0:
            df = df.replace({'OD': 'Seg. Odontológica', 'AMB': 'Seg. Ambulatorial', 'HCO': 'Seg. Hospitalar Com Obstetrícia', 'HSO': 'Seg. Hospitalar Sem Obstetrícia', 'REF': 'Plano Referência', 'PAC': 'Procedimento de Alta Complexidade', 'DUT': 'Diretriz de Utilização'})
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
    csv_base_name = 'Tabela'
    zip_file_name = "Teste_Pedro.zip"

    try:
        print(f"Iniciando processamento do arquivo: {pdf_path}")

        # 1. Extrair os dados das tabelas usando tabula-py
        print("Extraindo tabelas do PDF com tabula-py...")
        all_tables = extract_table_from_pdf_tabula(pdf_path)
        num_tables = len(all_tables)
        print(f"Foram encontradas {num_tables} tabelas.")

        if all_tables:
            all_dfs_processed = []
            for i, df in enumerate(all_tables):
                print(f"\n--- Tabela {i+1} ---")
                print(df.head())

                # 2. Substituir abreviações
                print("Substituindo abreviações...")
                df_processed = replace_abbreviations(df.copy())
                print("Abreviações substituídas com sucesso.")
                print(df_processed.head())
                all_dfs_processed.append(df_processed)

                # 3. Salvar em CSV
                csv_file = f"{csv_base_name}_{i+1}.csv"
                print(f"Salvando dados da Tabela {i+1} em '{csv_file}'...")
                save_to_csv(df_processed, csv_file)
                print(f"Dados da Tabela {i+1} salvos com sucesso em '{csv_file}'.")

                # 4. (Não é necessário compactar cada CSV individualmente para a tarefa)
                # O próximo passo é compactar todos os CSVs em um único ZIP

                print("-" * 30)

            # 5. Compactar todos os CSVs em um único ZIP
            if all_dfs_processed:
                with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i, _ in enumerate(all_dfs_processed):
                        csv_file = f"{csv_base_name}_{i+1}.csv"
                        if os.path.exists(csv_file):
                            zipf.write(csv_file, os.path.basename(csv_file))
                            print(f"Adicionado '{csv_file}' ao arquivo ZIP '{zip_file_name}'.")
                print(f"\nTodos os arquivos CSV foram compactados em '{zip_file_name}'.")
            else:
                print("Nenhuma tabela processada para compactação.")

        else:
            print("Nenhuma tabela foi encontrada para processamento.")

        print("\nProcessamento concluído!")

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
        # Limpeza (opcional)
        if 'all_tables' in locals():
            for i, _ in enumerate(all_tables):
                csv_file = f"{csv_base_name}_{i+1}.csv"
                if os.path.exists(csv_file):
                    print(f"Limpando arquivo temporário: {csv_file}")
                    os.remove(csv_file)

if __name__ == '__main__':
    try:
        import jpype
        print("jpype importado com sucesso.")
    except ImportError:
        print("Aviso: jpype não está instalado. Tente instalar com 'pip install jpype1'.")

    main()