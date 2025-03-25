import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.parse import urljoin

# URL de acesso ao site do GOV
url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'

# Função para obter os links dos PDFs
def get_pdf_links(url):
    # Requisição ao site
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Lista para armazenar os links dos PDFs, com base na tag <a> e no atributo href
    pdf_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Verificar se o link é um PDF e começa com "Anexo"
        if href.endswith('.pdf') and 'Anexo' in href:
            # Se o link for relativo, converte para absoluto
            full_url = urljoin(url, href)
            pdf_links.append(full_url)
    
    return pdf_links

# Função para baixar o PDF
def download_pdf(pdf_url, destination_folder):
    # Checagem se a pasta de destino existe, caso não, cria a pasta
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Obter o nome do arquivo a partir do link (extraindo o nome do arquivo da URL)
    file_name = pdf_url.split('/')[-1]
    file_path = os.path.join(destination_folder, file_name)
    
    # Realizar o download do arquivo PDF
    response = requests.get(pdf_url)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    
    return file_path

# Função para comprimir os arquivos baixados em um arquivo ZIP
def compress_to_zip(destination_folder, zip_file):
    with ZipFile(zip_file, 'w') as zipf:
        for root, dirs, files in os.walk(destination_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), destination_folder))

# Função principal
def main():
    destination_folder = 'pdf_files'
    zip_file = 'anexos.zip'
    
    # 1° passo: Obter os links dos PDFs
    pdf_links = get_pdf_links(url)
    print(f'Links encontrados: {pdf_links}')
    
    # 2° passo: Baixar os PDFs
    downloaded_files = []
    for link in pdf_links:
        downloaded_file = download_pdf(link, destination_folder)
        downloaded_files.append(downloaded_file)
        print(f'Arquivo baixado: {downloaded_file}')
    
    # 3° passo: Comprimir os arquivos baixados em um arquivo ZIP
    compress_to_zip(destination_folder, zip_file)
    print(f'Arquivo zip criado: {zip_file}')

if __name__ == '__main__':
    main()
