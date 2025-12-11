import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask, request, redirect, url_for
import logging
import db
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, '..', 'templates'),
    static_folder=os.path.join(BASE_DIR, '..', 'static'))
# Start page
@APP.route('/')
def index():
    stats = db.execute('''
        SELECT COUNT(*) as n_contratos,
        ROUND(SUM(precoContratual), 2) AS total_valor
        from contrato
    ''').fetchone()
    return render_template('index.html', stats=stats)

@APP.route('/contratos/')
def listar_contratos():
    rows = db.execute('''
        SELECT idContrato, objetoContrato, precoContratual, dataCelebracaoContrato 
        FROM contrato
        ORDER BY dataCelebracaoContrato DESC    
    ''').fetchall()
    return render_template('contratos.html', contratos=rows)

@APP.route('/contratos/<int:idcontrato>/')
def contrato(idcontrato):
    contrato = db.execute('''
        SELECT *
        FROM contrato
        WHERE idcontrato = ?
    ''',(idcontrato,)).fetchone()
    return render_template('contrato.html', c=contrato, voltar=request.referrer)

@APP.route('/Q1/')
def listar_tipos():
    tipos = db.execute('''
        SELECT nome
        FROM tipo_contrato
        order by nome
    ''').fetchall()
    return render_template('Q1.html', tipos=tipos)

@APP.route('/Q2/')
def entidade_F():
    entidade = db.execute('''
        select e.designacao
        from entidade e
        where e.designacao LIKE 'F%'
    ''').fetchall()
    return render_template('Q2.html', entidade=entidade)

@APP.route('/Q3/')
def preco_paises():
    preco = db.execute('''
        SELECT 
            p.nome AS pais,
            SUM(c.precoContratual) AS total_preco
        FROM contrato c
        JOIN contrato_local_execucao cle 
            ON c.idContrato = cle.idContrato
        JOIN municipio m 
            ON cle.municipio_id = m.municipio_id
        JOIN distrito d 
            ON m.distrito_id = d.distrito_id
        JOIN pais p 
            ON d.pais_id = p.pais_id
        GROUP BY p.nome
    ''').fetchall()
    return render_template('Q3.html', preco=preco)

@APP.route('/Q4/')
def ncontrato_tipo():
    quant = db.execute('''
    SELECT tc.nome,
       COUNT(c.idContrato) AS quantidade
    FROM contrato c
        JOIN
        ClassificacaoContratos ctc ON c.idContrato = ctc.idContrato
        JOIN
        tipo_contrato tc ON ctc.tipoContrato_id = tc.tipoContrato_id
    GROUP BY tc.tipoContrato_id
    ''').fetchall()
    return render_template('Q4.html', quant=quant)

@APP.route('/Q5/')
def contratos_por_entidade():
    dados = db.execute('''
    SELECT e.designacao AS entidade,
       COUNT(c.idContrato) AS total
    FROM contrato c
        JOIN
        entidade e ON c.adjudicante_id = e.entidade_id
    GROUP BY c.adjudicante_id
    ORDER BY total DESC
    ''').fetchall()
    return render_template('Q5.html', dados=dados)

@APP.route('/Q6/')
def media_preco_tipo_procedimento():
    dados = db.execute('''
    SELECT tp.descricao AS procedimento,
           ROUND(AVG(c.precoContratual), 2) AS media_preco
    FROM contrato c
    JOIN tipo_procedimento tp ON c.tipoProcedimento_id = tp.tipoProcedimento_id
    GROUP BY tp.tipoProcedimento_id
    ''').fetchall()
    return render_template('Q6.html', dados=dados)

@APP.route('/Q7/')
def contratos_por_mes():
    dados = db.execute('''
    SELECT SUBSTR(c.dataCelebracaoContrato, 6, 2) AS mes,
           COUNT(*) AS total
    FROM contrato c
    GROUP BY mes
    ORDER BY mes
    ''').fetchall()
    return render_template('Q7.html', dados=dados)

@APP.route('/Q8/')
def contratos_acima_media_global():
    dados = db.execute('''
    WITH media_global AS (
        SELECT AVG(precoContratual) AS mg FROM contrato
    )
    SELECT c.idContrato,
           e.designacao AS entidade,
           c.precoContratual
    FROM contrato c
    JOIN entidade e ON c.adjudicante_id = e.entidade_id 
    WHERE c.precoContratual > (SELECT mg FROM media_global)
    ORDER BY c.precoContratual DESC
    ''').fetchall()
    return render_template('Q8.html', dados=dados)

@APP.route('/Q9/')
def contratos_caros_cpv():
    dados = db.execute('''
    SELECT c.idContrato,
        c.precoContratual,
        cpv.designacao AS cpv_nome
    FROM contrato c
    JOIN possui p ON c.idContrato = p.idContrato
    JOIN cpv ON p.cpv_id = cpv.cpv_id
    ORDER BY c.precoContratual DESC
    LIMIT 10
    ''').fetchall()
    return render_template('Q9.html', dados=dados)

@APP.route('/Q10/')
def municipios_top_contratos():
    dados = db.execute('''
    WITH contratos_por_municipio AS (
        SELECT DISTINCT idContrato, municipio_id
        FROM contrato_local_execucao
    )
    SELECT m.nome AS municipio,
           ROUND(SUM(c.precoContratual), 2) AS total
    FROM contratos_por_municipio cm
    JOIN contrato c ON cm.idContrato = c.idContrato
    JOIN municipio m ON cm.municipio_id = m.municipio_id
    GROUP BY m.municipio_id
    ORDER BY total DESC
    LIMIT 10
    ''').fetchall()
    return render_template('Q10.html', dados=dados)

#Pesquisa do cabeçalho
@APP.route('/pesquisar')
def pesquisar():
    #Obter IDContrato da pesquisa
    query = request.args.get('q') 
    
    if query and query.isdigit():
        #Verifica se ID existe
        contrato = db.execute('''
            SELECT idContrato FROM contrato WHERE idContrato = ?
        ''', (query,)).fetchone()
        
        # Se o contrato for encontrado, redireciona para a página dele
        if contrato:
            return redirect(url_for('contrato', idcontrato=query))
    
    #Caso nao seja encontrado volta para a pagina
    return redirect(request.referrer or '/')

