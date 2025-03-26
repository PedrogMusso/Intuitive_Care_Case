import pandas as pd
import tabula
import zipfile
import os
from typing import List, Optional

class PDFTableProcessor:
    """
    Classe para processar tabelas de PDF e gerar um único CSV consolidado.
    """
    
    # Mapeamento específico para colunas OD e AMB
    COLUMN_ABBREVIATIONS = {
        'OD': 'Seg. Odontológica',
        'AMB': 'Seg. Ambulatorial'
    }
    
    def __init__(self, pdf_path: str, output_name: str):
        """
        Inicializa o processador com caminhos de entrada/saída.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            output_name: Nome base para os arquivos de saída
        """
        self.pdf_path = pdf_path
        self.output_name = output_name
        self.validate_paths()
        
    def validate_paths(self) -> None:
        """Valida os caminhos de arquivo fornecidos."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {self.pdf_path}")
        if not self.pdf_path.lower().endswith('.pdf'):
            raise ValueError("O arquivo de entrada deve ser um PDF")
            
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extrai todas as tabelas do PDF.
        
        Returns:
            Lista de DataFrames com as tabelas extraídas
        """
        try:
            print(f"Extraindo tabelas do PDF: {self.pdf_path}")
            tables = tabula.read_pdf(
                self.pdf_path,
                pages='all',
                multiple_tables=True,
                guess=True,
                silent=True
            )
            return tables if tables else []
        except Exception as e:
            raise Exception(f"Falha ao extrair tabelas: {str(e)}")
    
    def process_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa colunas específicas substituindo abreviações.
        
        Args:
            df: DataFrame a ser processado
            
        Returns:
            DataFrame processado
        """
        processed_df = df.copy()
        
        # Verifica quais colunas alvo existem no DataFrame
        target_cols = [col for col in ['OD', 'AMB'] if col in processed_df.columns]
        
        for col in target_cols:
            processed_df[col] = processed_df[col].apply(
                lambda x: self.COLUMN_ABBREVIATIONS.get(x, x) if pd.notna(x) else x
            )
        
        return processed_df
    
    def create_consolidated_csv(self, tables: List[pd.DataFrame]) -> str:
        """
        Cria um único CSV consolidado com tabelas separadas por linhas.
        
        Args:
            tables: Lista de DataFrames a serem consolidados
            
        Returns:
            Nome do arquivo CSV gerado
        """
        csv_filename = f"{self.output_name}.csv"
        
        try:
            with open(csv_filename, 'w', encoding='utf-8-sig') as f:
                for i, table in enumerate(tables):
                    # Processa as colunas específicas
                    processed_table = self.process_columns(table)
                    
                    # Escreve a tabela no arquivo
                    processed_table.to_csv(f, index=False, mode='a')
                    
                    # Adiciona linhas em branco entre tabelas (exceto após a última)
                    if i < len(tables) - 1:
                        f.write('\n' * 2)  # 2 linhas em branco
                        
            print(f"CSV consolidado criado: {csv_filename}")
            return csv_filename
        except Exception as e:
            raise Exception(f"Falha ao criar CSV consolidado: {str(e)}")
    
    def create_zip(self, csv_file: str) -> str:
        """
        Compacta o arquivo CSV em um ZIP.
        
        Args:
            csv_file: Arquivo CSV para compactar
            
        Returns:
            Nome do arquivo ZIP gerado
        """
        zip_filename = f"{self.output_name}.zip"
        
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(csv_file, os.path.basename(csv_file))
            print(f"Arquivo ZIP criado: {zip_filename}")
            return zip_filename
        except Exception as e:
            raise Exception(f"Falha ao criar arquivo ZIP: {str(e)}")
    
    def cleanup(self, file_to_remove: str) -> None:
        """Remove arquivo temporário."""
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)
            print(f"Arquivo temporário removido: {file_to_remove}")
    
    def execute(self) -> str:
        """
        Executa o fluxo completo de processamento.
        
        Returns:
            Nome do arquivo ZIP gerado
        """
        csv_file = None
        
        try:
            # Extrai tabelas do PDF
            tables = self.extract_tables()
            
            if not tables:
                raise ValueError("Nenhuma tabela encontrada no PDF")
            
            print(f"Processando {len(tables)} tabelas...")
            
            # Cria CSV consolidado
            csv_file = self.create_consolidated_csv(tables)
            
            # Cria arquivo ZIP
            zip_file = self.create_zip(csv_file)
            
            return zip_file
            
        except Exception as e:
            print(f"Erro durante o processamento: {str(e)}")
            raise
        finally:
            # Limpeza
            if csv_file and os.path.exists(csv_file):
                self.cleanup(csv_file)


if __name__ == '__main__':
    try:
        # Configuração
        PDF_PATH = 'WebScrapping/pdf_files/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf'
        OUTPUT_BASE = 'Teste_Pedro'
        
        # Executa o processamento
        processor = PDFTableProcessor(PDF_PATH, OUTPUT_BASE)
        zip_filename = processor.execute()
        
        print(f"\nProcesso concluído com sucesso! Arquivo gerado: {zip_filename}")
    
    except Exception as e:
        print(f"\nFalha no processamento: {str(e)}")
        exit(1)