from flask import Flask, request, jsonify
from flask_cors import CORS
from data_loader import load_operadoras_data

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita CORS (Cross-Origin Resource Sharing) para permitir requisições de diferentes origens
CORS(app)

# Carrega os dados das operadoras uma vez durante a inicialização do servidor
# Os dados já são pré-processados e ordenados por relevância no data_loader.py
df_operadoras = load_operadoras_data()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'OK' if not df_operadoras.empty else 'ERROR',  # Verifica se os dados foram carregados
        'records_loaded': len(df_operadoras),  # Retorna o total de registros carregados
        'columns': list(df_operadoras.columns) if not df_operadoras.empty else []  # Lista as colunas disponíveis
    })

@app.route('/api/operadoras', methods=['GET'])
def list_operadoras():
    """
    Endpoint para listagem paginada das operadoras
    Retorna as operadoras ordenadas por relevância (15 por página)
    """
    if df_operadoras.empty:
        return jsonify({'error': 'Dados não carregados'}), 500  # Erro se os dados não estiverem carregados
    
    try:
        # Obtém o número da página da query string (padrão: 1)
        page = int(request.args.get('page', 1))
        per_page = 15  # Define 15 itens por página
        
        # Calcula os índices para a paginação
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Seleciona os registros da página atual (já ordenados por relevância)
        results = df_operadoras.iloc[start_idx:end_idx]
        # Calcula o total de páginas necessárias
        total_pages = (len(df_operadoras) // per_page) + 1
        
        # Retorna os dados com metadados de paginação
        return jsonify({
            'data': results.to_dict(orient='records'),  # Dados em formato de dicionário
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': len(df_operadoras),
                'total_pages': total_pages
            }
        })
        
    except Exception as e:
        # Retorna erro 500 em caso de exceção
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_operadoras():
    """
    Endpoint de busca textual nas operadoras
    Busca nos campos: Razao_Social, Nome_Fantasia, Registro_ANS e CNPJ
    """
    if df_operadoras.empty:
        return jsonify({'error': 'Dados não carregados'}), 500
        
    # Obtém o termo de busca da query string e faz pré-processamento
    search_term = request.args.get('q', '').strip().lower()
    
    # Retorna vazio se o termo for muito curto
    if not search_term or len(search_term) < 2:
        return jsonify([])
    
    try:
        # Cria máscara booleana para filtrar os dados:
        # Verifica se o termo aparece em qualquer um dos campos importantes
        mask = (
            df_operadoras['Razao_Social'].str.lower().str.contains(search_term, na=False) |
            df_operadoras['Nome_Fantasia'].str.lower().str.contains(search_term, na=False) |
            df_operadoras['Registro_ANS'].astype(str).str.lower().str.contains(search_term, na=False) |
            df_operadoras['CNPJ'].astype(str).str.lower().str.contains(search_term, na=False)
        )
        
        # Aplica a máscara e limita a 50 resultados
        results = df_operadoras[mask].head(50)
        # Retorna os resultados em formato JSON
        return jsonify(results.to_dict(orient='records'))
    
    except Exception as e:
        # Retorna erro 500 em caso de exceção
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicia o servidor Flask
    # host='0.0.0.0' torna a API acessível em toda a rede
    # debug=True ativa o modo de desenvolvimento (não usar em produção)
    app.run(host='0.0.0.0', port=5000, debug=True)