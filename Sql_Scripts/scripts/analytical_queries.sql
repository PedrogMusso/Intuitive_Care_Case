-- 1. Cria índice temporário para otimização
CREATE INDEX IF NOT EXISTS tmp_idx_conta_desc ON demonstracoes_contabeis(cd_conta_contabil, descricao);

-- 2. Consulta para o último trimestre
WITH conta_eventos AS (
    SELECT DISTINCT cd_conta_contabil
    FROM demonstracoes_contabeis
    WHERE descricao ILIKE '%eventos/%medico hospitalar%'
       OR descricao ILIKE '%sinistros conhecidos%'
    LIMIT 1
),
periodo_trimestre AS (
    SELECT 
        MAX(data) AS data_final,
        MAX(data) - INTERVAL '3 months' AS data_inicial
    FROM demonstracoes_contabeis
)
SELECT 
    o.razao_social,
    o.nome_fantasia,
    SUM(d.vl_saldo_final - d.vl_saldo_inicial) AS total_despesas,
    TO_CHAR(SUM(d.vl_saldo_final - d.vl_saldo_inicial), 'L999G999G990D99') AS despesas_formatadas
FROM 
    demonstracoes_contabeis d
JOIN 
    operadoras o ON d.reg_ans = o.registro_ans
CROSS JOIN
    conta_eventos, periodo_trimestre
WHERE 
    d.cd_conta_contabil = conta_eventos.cd_conta_contabil
    AND d.data BETWEEN periodo_trimestre.data_inicial AND periodo_trimestre.data_final
GROUP BY 
    o.razao_social, o.nome_fantasia
ORDER BY 
    total_despesas DESC
LIMIT 10;

-- 3. Remove índice temporário
DROP INDEX IF EXISTS tmp_idx_conta_desc;