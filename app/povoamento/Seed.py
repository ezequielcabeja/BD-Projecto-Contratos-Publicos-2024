import sqlite3
import pandas as pd
import re

# Nomde dos ficheiros e base de dados
DB_NAME = "contratos_publicos.db"
EXCEL_FILE = "ContratosPublicos2024.xlsx"

# Ler Excel
df = pd.read_excel(EXCEL_FILE)

# Converter preço para float
if "precoContratual" in df.columns:
    df["precoContratual"] = (
        df["precoContratual"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .apply(pd.to_numeric, errors='coerce')
    )

#Conexão com a base de dados
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# --- FUNÇÕES AUXILIARES ---

def parse_fundamentacao(texto):
    #Extrai campos (Artigo, n.º, Alínea, Ref. Legislativa) de um texto complexo
    if pd.isna(texto) or texto is None:
        return None
    artigo = numero = alinea = subalinea = refLegislativa = None
    
    m = re.search(r"Artigo\s+([\dº\.]+)", texto, re.IGNORECASE)
    if m: artigo = m.group(1) #Extrai o Artigo
    m = re.search(r"n\.º\s+(\d+)", texto, re.IGNORECASE)
    if m: numero = m.group(1) #Extrai o Número
    m = re.search(r"alínea\s+([a-z]\))", texto, re.IGNORECASE)
    if m: alinea = m.group(1) #Extrai alínea
    m = re.search(r"subalínea\s+([ivx]+\))", texto, re.IGNORECASE)
    if m: subalinea = m.group(1) #Extrai subalínea
    m = re.search(r"do\s+(.*)$", texto, re.IGNORECASE)
    if m: refLegislativa = m.group(1).strip() #Extrai restante como Ref. Legislativa
    
    return artigo, numero, alinea, subalinea, refLegislativa

def parse_tipo_contrato(raw):
    #Separa múltiplos tipos de contrato (delimitados por |) numa lista
    if pd.isna(raw): return []
    return [t.strip() for t in raw.split("|") if t.strip()]

def safe_date(x):
    #Garante que a data está no formato de string aceitável ou é NONE
    if pd.isna(x): return None
    if isinstance(x, str): return x.strip()
    try: return x.strftime("%Y-%m-%d")
    except: return str(x)

def parse_entidade(raw):
    #Converte 'NIF - Nome' em (nif, nome)
    if pd.isna(raw): return None, None
    raw = str(raw).strip()
    if " - " not in raw:
        return None, raw # Sem NIF
    
    parts = raw.split(" - ", 1)
    try:
        nif = int(parts[0].strip()) #converte NIF para inteiro
        nome = parts[1].strip()
        return nif, nome
    except:
        return None, raw

def split_adjudicatarios(raw):
    #Separa vários Adjudicatários (delimitados por | ou ;) numa lista.
    if pd.isna(raw): return []
    texto = str(raw)
    partes = re.split(r'[;|]', texto)
    return [p.strip() for p in partes if p.strip()]

def parse_cpv(raw):
    #Separa o Código CPV da sua Descrição (formato 'Código - Descrição').
    if pd.isna(raw): return None, None
    if " - " not in raw: return raw.strip(), None
    cod, desc = raw.split(" - ", 1)
    return cod.strip(), desc.strip()

def parse_local_execucao(raw):
    #Extrai País, Distrito e Município de uma string complexa de Localização.
    if pd.isna(raw): return []
    locais = []
    grupos = [g.strip() for g in str(raw).split("|")]
    for g in grupos:
        partes = [p.strip() for p in g.split(",")]
        #Mapeia as partes extraídas para (País, Distrito, Município)
        if len(partes) >= 3:
            locais.append((partes[0], partes[1], partes[2]))
        elif len(partes) == 2:
            locais.append((partes[0], partes[1], "Desconhecido"))
        elif len(partes) == 1:
            locais.append((partes[0], "Desconhecido", "Desconhecido"))
    return locais

# --- FUNÇÕES DE INSERÇÃO NA BASE DE DADOS ---

def insert_return_id(sql_insert, params, sql_select, select_params):
    #Tenta encontrar um registo na BD
    cur.execute(sql_select, select_params)
    row = cur.fetchone()
    if row: return row[0]
    cur.execute(sql_insert, params)
    return cur.lastrowid

def insert_entidade(nif, nome):
    #Insere ou atualiza uma Entidade (Adjudicante ou Adjudicatário) na tabela 'entidade'
    if not nome: return None

    #Encontrar NIF se existir
    if nif:
        cur.execute("SELECT entidade_id FROM entidade WHERE nif = ?", (nif,))
        row = cur.fetchone()
        if row: return row[0]

    #Tentar encontrar por nome por empresas com nif em falta
    cur.execute("SELECT entidade_id FROM entidade WHERE designacao = ?", (nome,))
    row = cur.fetchone()
    
    if row:
        existing_id = row[0]
        #Encontrámos pelo nome e agora temos um NIF, atualizamos o registo
        if nif:
            cur.execute("UPDATE entidade SET nif = ? WHERE entidade_id = ?", (nif, existing_id))
        return existing_id

    #Novo
    if nif:
        cur.execute("INSERT INTO entidade (nif, designacao) VALUES (?, ?)", (nif, nome))
    else:
        cur.execute("INSERT INTO entidade (designacao) VALUES (?)", (nome,))
        
    return cur.lastrowid

counter = 0
for _, row in df.iterrows():
    counter += 1
    # CPVs
    lista_cpv_ids = []
    if not pd.isna(row["cpv"]):
        partes = [p.strip() for p in str(row["cpv"]).split("|")]
        for cpv_raw in partes:
            cod, desc = parse_cpv(cpv_raw)
            if cod:
                c_id = insert_return_id(
                    "INSERT INTO cpv (codigo, designacao) VALUES (?, ?)", (cod, desc),
                    "SELECT cpv_id FROM cpv WHERE codigo = ?", (cod,)
                )
                lista_cpv_ids.append(c_id)

    # Local Execução
    lista_locais = parse_local_execucao(row["localExecucao"])
    municipios_ids = []
    for pais, distrito, municipio in lista_locais:
        p_id = insert_return_id("INSERT INTO pais (nome) VALUES (?)", (pais,), "SELECT pais_id FROM pais WHERE nome = ?", (pais,))
        d_id = insert_return_id("INSERT INTO distrito (nome, pais_id) VALUES (?, ?)", (distrito, p_id), "SELECT distrito_id FROM distrito WHERE nome = ? AND pais_id = ?", (distrito, p_id))
        m_id = insert_return_id("INSERT INTO municipio (nome, distrito_id) VALUES (?, ?)", (municipio, d_id), "SELECT municipio_id FROM municipio WHERE nome = ? AND distrito_id = ?", (municipio, d_id))
        municipios_ids.append(m_id)

    # Adjudicante
    adj_nif, adj_nome = parse_entidade(row["adjudicante"])
    adjudicante_id = insert_entidade(adj_nif, adj_nome)

    # Adjudicatários
    adjudicatarios_ids = []
    if not pd.isna(row["adjudicatarios"]):
        lista = split_adjudicatarios(row["adjudicatarios"]) 
        for item in lista:
            nif, nome = parse_entidade(item)
            ent_id = insert_entidade(nif, nome)
            if ent_id:
                adjudicatarios_ids.append(ent_id)

    # Acordo Quadro
    acordoQuadro_id = None
    if not pd.isna(row["DescrAcordoQuadro"]):
        acordoQuadro_id = insert_return_id(
            "INSERT INTO acordo_quadro (descrAcordoQuadro) VALUES (?)", (row["DescrAcordoQuadro"],),
            "SELECT acordoQuadro_id FROM acordo_quadro WHERE descrAcordoQuadro = ?", (row["DescrAcordoQuadro"],)
        )

    # Procedimento
    tp_id = None
    if not pd.isna(row["tipoprocedimento"]):
        tp_id = insert_return_id(
            "INSERT INTO tipo_procedimento (descricao) VALUES (?)", (row["tipoprocedimento"],),
            "SELECT tipoProcedimento_id FROM tipo_procedimento WHERE descricao = ?", (row["tipoprocedimento"],)
        )

    # Fundamentação
    fundamento = parse_fundamentacao(row["fundamentacao"])
    id_fundamentacao = None
    if fundamento:
        art, num, ali, sub, ref = fundamento
        # Só insere se tiver pelo menos Artigo ou RefLegislativa
        if art or ref: 
            id_fundamentacao = insert_return_id(
                "INSERT INTO fundamentacao (artigo, numero, alinea, subalinea, refLegislativa) VALUES (?, ?, ?, ?, ?)",
                (art, num, ali, sub, ref),
                "SELECT id_Fundamentacao FROM fundamentacao WHERE artigo IS ? AND numero IS ? AND alinea IS ? AND subalinea IS ? AND refLegislativa IS ?",
                (art, num, ali, sub, ref)
            )

    # CONTRATO
    try:
        cur.execute("""
            INSERT OR REPLACE INTO contrato (
                idContrato, objetoContrato, dataPublicacao, dataCelebracaoContrato, 
                precoContratual, prazoExecucao, procedimentoCentralizado,
                adjudicante_id, tipoProcedimento_id, acordoQuadro_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["idcontrato"], row["objectoContrato"], safe_date(row["dataPublicacao"]),
            safe_date(row["dataCelebracaoContrato"]), row["precoContratual"], row["prazoExecucao"],
            1 if row["ProcedimentoCentralizado"] == 'Sim' else 0,
            adjudicante_id, tp_id, acordoQuadro_id
        ))
    except sqlite3.IntegrityError as e:
        print(f"Erro no contrato {row['idcontrato']}: {e}")
        continue

    # Relações N:M 

    #Adjudicatarios (Contrato -> Entidade)
    for ent_id in adjudicatarios_ids:
        cur.execute("INSERT OR IGNORE INTO adjudicatario_contrato (idContrato, entidade_id) VALUES (?, ?)", (row["idcontrato"], ent_id))

    #Locais de Execução (Contrato -> Município)
    for m_id in municipios_ids:
        cur.execute("INSERT OR IGNORE INTO contrato_local_execucao (idContrato, municipio_id) VALUES (?, ?)", (row["idcontrato"], m_id))

    #Tipos de Contrato (Contrato -> Tipo de Contrato)
    tipos = parse_tipo_contrato(row["tipoContrato"])
    for t in tipos:
        t_id = insert_return_id("INSERT INTO tipo_contrato (nome) VALUES (?)", (t,), "SELECT tipoContrato_id FROM tipo_contrato WHERE nome = ?", (t,))
        cur.execute("INSERT OR IGNORE INTO ClassificacaoContratos (idContrato, tipoContrato_id) VALUES (?, ?)", (row["idcontrato"], t_id))

    #Fundamentação (Contrato -> Fundamentação)
    if id_fundamentacao:
        cur.execute("INSERT OR IGNORE INTO fundamentacao_contrato (idContrato, id_Fundamentacao) VALUES (?, ?)", (row["idcontrato"], id_fundamentacao))
    
    #CPVs (Contrato -> CPV)
    for c_id in lista_cpv_ids:
        cur.execute("INSERT OR IGNORE INTO possui (idContrato, cpv_id) VALUES (?, ?)", (row["idcontrato"], c_id))

conn.commit()
conn.close()
print("Inserção concluída")