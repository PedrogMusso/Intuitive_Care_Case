-- Script de importação para PostgreSQL com encoding LATIN1
-- import_data.sql

-- 1. Remove constraints temporariamente para permitir importação flexível
ALTER TABLE demonstracoes_contabeis DROP CONSTRAINT IF EXISTS demonstracoes_contabeis_reg_ans_fkey;

-- 2. Função para conversão de números no formato brasileiro
CREATE OR REPLACE FUNCTION converter_numero_br(text) RETURNS numeric AS $$
BEGIN
    RETURN CASE 
        WHEN $1 IS NULL OR $1 = '' THEN NULL
        ELSE REPLACE(REPLACE($1, '.', ''), ',', '.')::numeric
    END;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 3. Importação dos dados cadastrais das operadoras
\echo 'Importando dados cadastrais...'
COPY operadoras(
    registro_ans, cnpj, razao_social, nome_fantasia, modalidade,
    logradouro, numero, complemento, bairro, cidade, uf, cep,
    ddd, telefone, fax, endereco_eletronico, representante,
    cargo_representante, regiao_comercializacao, data_registro_ans
) 
FROM '/csv_files/Relatorio_cadop.csv' 
WITH (
    FORMAT CSV,
    DELIMITER ';',
    HEADER TRUE,
    ENCODING 'LATIN1',
    NULL ''
);

-- 4. Importação dos dados trimestrais em duas etapas
\echo 'Importando dados trimestrais...'

-- Etapa 1: Cria tabela temporária para importação inicial
CREATE TEMPORARY TABLE temp_dados_trimestrais (
    data text,
    reg_ans text,
    cd_conta_contabil text,
    descricao text,
    vl_saldo_inicial text,
    vl_saldo_final text
);

-- Importa todos os arquivos trimestrais para a tabela temporária
COPY temp_dados_trimestrais FROM '/csv_files/1T2023.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/2T2023.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/3T2023.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/4T2023.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/1T2024.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/2T2024.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/3T2024.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');
COPY temp_dados_trimestrais FROM '/csv_files/4T2024.csv' WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE, ENCODING 'LATIN1');

-- Etapa 2: Filtra e converte os dados para a tabela definitiva
INSERT INTO demonstracoes_contabeis (
    data, reg_ans, cd_conta_contabil, descricao, 
    vl_saldo_inicial, vl_saldo_final
)
SELECT 
    CASE 
        WHEN data ~ '^\d{2}/\d{2}/\d{4}$' THEN to_date(data, 'DD/MM/YYYY')
        WHEN data ~ '^\d{4}-\d{2}-\d{2}$' THEN to_date(data, 'YYYY-MM-DD')
        ELSE NULL
    END,
    reg_ans,
    cd_conta_contabil,
    descricao,
    converter_numero_br(vl_saldo_inicial),
    converter_numero_br(vl_saldo_final)
FROM temp_dados_trimestrais
WHERE 
    -- Filtra apenas registros com dados válidos
    (data ~ '^\d{2}/\d{2}/\d{4}$' OR data ~ '^\d{4}-\d{2}-\d{2}$')
    AND reg_ans ~ '^\d+$';

-- 5. Recria a constraint de chave estrangeira com tratamento para registros órfãos
ALTER TABLE demonstracoes_contabeis 
ADD CONSTRAINT demonstracoes_contabeis_reg_ans_fkey 
FOREIGN KEY (reg_ans) REFERENCES operadoras(registro_ans)
ON DELETE SET NULL;

-- 6. Verificação dos dados importados
\echo 'Verificação pós-importação:'
SELECT COUNT(*) AS total_operadoras FROM operadoras;
SELECT COUNT(*) AS registros_financeiros_importados FROM demonstracoes_contabeis;
SELECT COUNT(*) AS registros_com_problemas FROM temp_dados_trimestrais 
WHERE NOT (data ~ '^\d{2}/\d{2}/\d{4}$' OR data ~ '^\d{4}-\d{2}-\d{2}$');
SELECT MIN(data) AS data_inicial, MAX(data) AS data_final FROM demonstracoes_contabeis;

-- 7. Limpeza
DROP TABLE temp_dados_trimestrais;
\echo 'Importação concluída com sucesso!';