-- Remove o banco de dados existente para recriação limpa
DROP DATABASE IF EXISTS ans_db;
CREATE DATABASE ans_db;

\c ans_db

-- Tabela de operadoras com estrutura corrigida
CREATE TABLE operadoras (
    registro_ans VARCHAR(20) PRIMARY KEY,
    cnpj VARCHAR(18),
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    cep VARCHAR(10),
    ddd VARCHAR(4),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    endereco_eletronico VARCHAR(100),
    representante VARCHAR(100),
    cargo_representante VARCHAR(100),
    regiao_comercializacao VARCHAR(100),
    data_registro_ans DATE
);

-- Tabela de demonstrações contábeis com estrutura corrigida
CREATE TABLE demonstracoes_contabeis (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    reg_ans VARCHAR(20) NOT NULL,
    cd_conta_contabil VARCHAR(20),
    descricao VARCHAR(255) NOT NULL,
    vl_saldo_inicial DECIMAL(15,2),
    vl_saldo_final DECIMAL(15,2),
    FOREIGN KEY (reg_ans) REFERENCES operadoras(registro_ans)
);

-- Índices para otimização
CREATE INDEX idx_demconta_reg_ans ON demonstracoes_contabeis(reg_ans);
CREATE INDEX idx_demconta_data ON demonstracoes_contabeis(data);
CREATE INDEX idx_demconta_conta ON demonstracoes_contabeis(cd_conta_contabil);