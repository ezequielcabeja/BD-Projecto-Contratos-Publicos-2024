import sqlite3

DB_NAME = "contratos_publicos.db"
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS possui;
DROP TABLE IF EXISTS fundamentacao_contrato;  
DROP TABLE IF EXISTS ClassificacaoContratos;
DROP TABLE IF EXISTS contrato_local_execucao;
DROP TABLE IF EXISTS adjudicatario_contrato;
DROP TABLE IF EXISTS contrato;
DROP TABLE IF EXISTS fundamentacao;
DROP TABLE IF EXISTS tipo_contrato;
DROP TABLE IF EXISTS tipo_procedimento;
DROP TABLE IF EXISTS acordo_quadro;
DROP TABLE IF EXISTS cpv;
DROP TABLE IF EXISTS entidade;
DROP TABLE IF EXISTS municipio;
DROP TABLE IF EXISTS distrito;
DROP TABLE IF EXISTS pais;
""")

cur.executescript("""

-- PAIS
CREATE TABLE pais (
    pais_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE
);

-- DISTRITO
CREATE TABLE distrito (
    distrito_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    pais_id INTEGER,
    UNIQUE(nome, pais_id),
    FOREIGN KEY(pais_id) REFERENCES pais(pais_id)
);

-- MUNICIPIO
CREATE TABLE municipio (
    municipio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    distrito_id INTEGER,
    UNIQUE(nome, distrito_id),
    FOREIGN KEY(distrito_id) REFERENCES distrito(distrito_id)
);

-- ENTIDADE 
CREATE TABLE entidade (
    entidade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nif INTEGER UNIQUE, 
    designacao TEXT
);

-- CPV
CREATE TABLE cpv (
    cpv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    designacao TEXT
);

-- ACORDO QUADRO
CREATE TABLE acordo_quadro (
    acordoQuadro_id INTEGER PRIMARY KEY AUTOINCREMENT,
    descrAcordoQuadro TEXT UNIQUE
);

-- TIPO CONTRATO
CREATE TABLE tipo_contrato (
    tipoContrato_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE
);

-- TIPO PROCEDIMENTO
CREATE TABLE tipo_procedimento (
    tipoProcedimento_id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT UNIQUE
);

-- FUNDAMENTAÇÃO
CREATE TABLE fundamentacao (
    id_Fundamentacao INTEGER PRIMARY KEY AUTOINCREMENT,
    artigo TEXT,
    numero TEXT,
    alinea TEXT,
    subalinea TEXT,
    refLegislativa TEXT,
    UNIQUE(artigo, numero, alinea, subalinea, refLegislativa)
);

-- CONTRATO
CREATE TABLE contrato (
    idContrato INTEGER PRIMARY KEY,
    objetoContrato TEXT NOT NULL,
    dataPublicacao TEXT,
    dataCelebracaoContrato TEXT,
    precoContratual REAL,
    prazoExecucao INTEGER,
    procedimentoCentralizado BOOLEAN,

    adjudicante_id INTEGER,
    tipoProcedimento_id INTEGER,
    acordoQuadro_id INTEGER,

    FOREIGN KEY(adjudicante_id) REFERENCES entidade(entidade_id),
    FOREIGN KEY(tipoProcedimento_id) REFERENCES tipo_procedimento(tipoProcedimento_id),
    FOREIGN KEY(acordoQuadro_id) REFERENCES acordo_quadro(acordoQuadro_id)
);

-- N:M ADJUDICATÁRIO
CREATE TABLE adjudicatario_contrato (
    idContrato INTEGER,
    entidade_id INTEGER,
    PRIMARY KEY(idContrato, entidade_id),
    FOREIGN KEY(idContrato) REFERENCES contrato(idContrato),
    FOREIGN KEY(entidade_id) REFERENCES entidade(entidade_id)
);

-- N:M LOCAL EXECUCAO
CREATE TABLE contrato_local_execucao (
    idContrato INTEGER,
    municipio_id INTEGER,
    PRIMARY KEY(idContrato, municipio_id),
    FOREIGN KEY(idContrato) REFERENCES contrato(idContrato),
    FOREIGN KEY(municipio_id) REFERENCES municipio(municipio_id)
);

-- N:M TIPO CONTRATO (NOVO NOME: ClassificacaoContratos)
CREATE TABLE ClassificacaoContratos (
    idContrato INTEGER,
    tipoContrato_id INTEGER,
    PRIMARY KEY(idContrato, tipoContrato_id),
    FOREIGN KEY(idContrato) REFERENCES contrato(idContrato),
    FOREIGN KEY(tipoContrato_id) REFERENCES tipo_contrato(tipoContrato_id)
);

-- N:M FUNDAMENTAÇÃO (NOVO NOME: fundamentacao_contrato)
CREATE TABLE fundamentacao_contrato (
    idContrato INTEGER,
    id_Fundamentacao INTEGER,
    PRIMARY KEY(idContrato, id_Fundamentacao),
    FOREIGN KEY(idContrato) REFERENCES contrato(idContrato),
    FOREIGN KEY(id_Fundamentacao) REFERENCES fundamentacao(id_Fundamentacao)
);

-- N:M CPV
CREATE TABLE possui (
    idContrato INTEGER,
    cpv_id INTEGER,
    PRIMARY KEY(idContrato, cpv_id),
    FOREIGN KEY(idContrato) REFERENCES contrato(idContrato),
    FOREIGN KEY(cpv_id) REFERENCES cpv(cpv_id)
);

""")

conn.commit()
conn.close()
print("Base de dados criada")