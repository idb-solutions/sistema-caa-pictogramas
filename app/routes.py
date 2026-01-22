"""
routes.py
Rotas da aplicação (API REST + Views)
Sistema de Comunicação Alternativa com Pictogramas para TEA
Instituto Tia Dani - Costa Rica/MS
"""

from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from app.models import db, Usuario, Paciente, Categoria, Pictograma, Sessao, HistoricoSelecao
from datetime import datetime
from sqlalchemy import desc
from functools import wraps

main = Blueprint('main', __name__)


# ========== DECORATOR DE AUTENTICAÇÃO ==========

def login_required(f):
    """Decorator para proteger rotas que exigem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            if request.is_json:
                return jsonify({'erro': 'Não autenticado'}), 401
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# ========== VIEWS HTML ==========

@main.route('/')
def index():
    """Página de Login"""
    if 'usuario_id' in session:
        return redirect(url_for('main.selecionar_paciente'))
    return render_template('login.html')


@main.route('/cadastro')
def cadastro():
    """Página de Cadastro de novo profissional"""
    return render_template('cadastro.html')


@main.route('/selecionar-paciente')
@login_required
def selecionar_paciente():
    """Página de seleção de paciente"""
    return render_template('selecionar_paciente.html')


@main.route('/comunicacao/<int:paciente_id>')
@login_required
def comunicacao(paciente_id):
    """Interface de comunicação com pictogramas"""
    paciente = Paciente.query.get_or_404(paciente_id)
    return render_template('comunicacao.html', paciente=paciente)


@main.route('/historico')
@login_required
def historico():
    """Página de histórico de sessões"""
    return render_template('historico.html')


@main.route('/gerenciar')
@login_required
def gerenciar():
    """Página de gerenciamento de categorias e pictogramas"""
    return render_template('gerenciar.html')


# ========== API - AUTENTICAÇÃO ==========

@main.route('/api/login', methods=['POST'])
def api_login():
    """Login de usuário - Recebe: { login, senha }"""
    dados = request.get_json()
    login = dados.get('login', '').strip()
    senha = dados.get('senha', '').strip()
    
    if not login or not senha:
        return jsonify({'erro': 'Login e senha são obrigatórios'}), 400
    
    usuario = Usuario.query.filter_by(login=login, ativo=True).first()
    
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 401
    
    if usuario.senha != senha:
        return jsonify({'erro': 'Senha incorreta'}), 401
    
    session['usuario_id'] = usuario.id
    session['usuario_nome'] = usuario.nome
    session['usuario_login'] = usuario.login
    
    return jsonify({
        'sucesso': True,
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'login': usuario.login,
            'cargo': usuario.cargo
        }
    })


@main.route('/api/cadastro', methods=['POST'])
def api_cadastro():
    """Cadastro de novo profissional"""
    dados = request.get_json()
    
    nome = dados.get('nome', '').strip()
    login = dados.get('login', '').strip()
    senha = dados.get('senha', '').strip()
    cargo = dados.get('cargo', '').strip()
    
    if not nome or not login or not senha:
        return jsonify({'erro': 'Nome, login e senha são obrigatórios'}), 400
    
    if len(senha) < 4:
        return jsonify({'erro': 'Senha deve ter pelo menos 4 dígitos'}), 400
    
    if not senha.isdigit():
        return jsonify({'erro': 'Senha deve conter apenas números'}), 400
    
    usuario_existente = Usuario.query.filter_by(login=login).first()
    if usuario_existente:
        return jsonify({'erro': 'Este login já está em uso'}), 400
    
    usuario = Usuario(nome=nome, login=login, senha=senha, cargo=cargo)
    
    db.session.add(usuario)
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Cadastro realizado com sucesso!'
    }), 201


@main.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout"""
    session.clear()
    return jsonify({'sucesso': True})


@main.route('/api/usuario/atual', methods=['GET'])
def api_usuario_atual():
    """Retorna dados do usuário logado"""
    if 'usuario_id' not in session:
        return jsonify({'logado': False}), 200
    
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario:
        session.clear()
        return jsonify({'logado': False}), 200
    
    return jsonify({
        'logado': True,
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'login': usuario.login,
            'cargo': usuario.cargo
        }
    })


# ========== API - PACIENTES ==========

@main.route('/api/pacientes', methods=['GET'])
@login_required
def api_listar_pacientes():
    """Lista pacientes do profissional logado"""
    usuario_id = session.get('usuario_id')
    
    pacientes = Paciente.query.filter_by(
        usuario_id=usuario_id,
        ativo=True
    ).order_by(Paciente.nome).all()
    
    return jsonify({
        'pacientes': [{
            'id': p.id,
            'nome': p.nome,
            'data_nascimento': p.data_nascimento.isoformat() if p.data_nascimento else None,
            'nivel_suporte': p.nivel_suporte,
            'foto_perfil': p.foto_perfil
        } for p in pacientes]
    })


@main.route('/api/pacientes', methods=['POST'])
@login_required
def api_criar_paciente():
    """Cria novo paciente"""
    usuario_id = session.get('usuario_id')
    dados = request.get_json()
    
    if not dados.get('nome'):
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    
    paciente = Paciente(
        nome=dados['nome'],
        data_nascimento=datetime.strptime(dados.get('data_nascimento'), '%Y-%m-%d').date() 
            if dados.get('data_nascimento') else None,
        diagnostico=dados.get('diagnostico'),
        nivel_suporte=dados.get('nivel_suporte'),
        preferencias=dados.get('preferencias'),
        foto_perfil=dados.get('foto_perfil'),
        usuario_id=usuario_id
    )
    
    db.session.add(paciente)
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'paciente': {'id': paciente.id, 'nome': paciente.nome}
    }), 201


@main.route('/api/pacientes/<int:paciente_id>', methods=['GET'])
@login_required
def api_obter_paciente(paciente_id):
    """Obtém dados de um paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    
    return jsonify({
        'id': paciente.id,
        'nome': paciente.nome,
        'data_nascimento': paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
        'diagnostico': paciente.diagnostico,
        'nivel_suporte': paciente.nivel_suporte,
        'foto_perfil': paciente.foto_perfil
    })


@main.route('/api/pacientes/<int:paciente_id>', methods=['PUT'])
@login_required
def api_atualizar_paciente(paciente_id):
    """Atualiza dados de um paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    dados = request.get_json()
    
    if dados.get('nome'):
        paciente.nome = dados['nome']
    if 'data_nascimento' in dados:
        paciente.data_nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date() if dados['data_nascimento'] else None
    if 'diagnostico' in dados:
        paciente.diagnostico = dados['diagnostico']
    if 'nivel_suporte' in dados:
        paciente.nivel_suporte = dados['nivel_suporte']
    
    db.session.commit()
    return jsonify({'sucesso': True})


@main.route('/api/pacientes/<int:paciente_id>', methods=['DELETE'])
@login_required
def api_excluir_paciente(paciente_id):
    """Desativa um paciente (soft delete)"""
    paciente = Paciente.query.get_or_404(paciente_id)
    paciente.ativo = False
    db.session.commit()
    return jsonify({'sucesso': True})


# ========== API - CATEGORIAS ==========

@main.route('/api/categorias', methods=['GET'])
def api_listar_categorias():
    """Lista todas as categorias"""
    categorias = Categoria.query.order_by(Categoria.ordem).all()
    
    return jsonify({
        'categorias': [{
            'id': c.id,
            'nome': c.nome,
            'cor': c.cor,
            'icone': c.icone,
            'ordem': c.ordem
        } for c in categorias]
    })


@main.route('/api/categorias', methods=['POST'])
@login_required
def api_criar_categoria():
    """Cria nova categoria"""
    dados = request.get_json()
    
    if not dados.get('nome'):
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    
    ultima = Categoria.query.order_by(desc(Categoria.ordem)).first()
    proxima_ordem = (ultima.ordem + 1) if ultima else 1
    
    categoria = Categoria(
        nome=dados['nome'],
        cor=dados.get('cor', '#4ECDC4'),
        icone=dados.get('icone', '📁'),
        ordem=dados.get('ordem', proxima_ordem)
    )
    
    db.session.add(categoria)
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'categoria': {'id': categoria.id, 'nome': categoria.nome}
    }), 201


@main.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
@login_required
def api_atualizar_categoria(categoria_id):
    """Atualiza uma categoria"""
    categoria = Categoria.query.get_or_404(categoria_id)
    dados = request.get_json()
    
    if dados.get('nome'):
        categoria.nome = dados['nome']
    if dados.get('cor'):
        categoria.cor = dados['cor']
    if dados.get('icone'):
        categoria.icone = dados['icone']
    if dados.get('ordem'):
        categoria.ordem = dados['ordem']
    
    db.session.commit()
    return jsonify({'sucesso': True})


@main.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
@login_required
def api_excluir_categoria(categoria_id):
    """Exclui uma categoria"""
    categoria = Categoria.query.get_or_404(categoria_id)
    Pictograma.query.filter_by(categoria_id=categoria_id).delete()
    db.session.delete(categoria)
    db.session.commit()
    return jsonify({'sucesso': True})


# ========== API - PICTOGRAMAS ==========

@main.route('/api/pictogramas', methods=['GET'])
def api_listar_pictogramas():
    """Lista pictogramas"""
    categoria_id = request.args.get('categoria_id', type=int)
    
    query = Pictograma.query.filter_by(ativo=True)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    pictogramas = query.order_by(Pictograma.ordem).all()
    
    return jsonify({
        'pictogramas': [{
            'id': p.id,
            'nome': p.nome,
            'imagem_url': p.imagem_url,
            'audio_texto': p.audio_texto,
            'categoria_id': p.categoria_id,
            'categoria_nome': p.categoria.nome,
            'categoria_cor': p.categoria.cor
        } for p in pictogramas]
    })


@main.route('/api/pictogramas', methods=['POST'])
@login_required
def api_criar_pictograma():
    """Cria novo pictograma"""
    dados = request.get_json()
    
    if not dados.get('nome') or not dados.get('categoria_id'):
        return jsonify({'erro': 'Nome e categoria são obrigatórios'}), 400
    
    categoria = Categoria.query.get(dados['categoria_id'])
    if not categoria:
        return jsonify({'erro': 'Categoria não encontrada'}), 404
    
    ultimo = Pictograma.query.filter_by(categoria_id=dados['categoria_id']).order_by(desc(Pictograma.ordem)).first()
    proxima_ordem = (ultimo.ordem + 1) if ultimo else 1
    
    pictograma = Pictograma(
        nome=dados['nome'],
        categoria_id=dados['categoria_id'],
        imagem_url=dados.get('imagem_url', '/static/images/placeholder.png'),
        audio_texto=dados.get('audio_texto', dados['nome']),
        ordem=dados.get('ordem', proxima_ordem)
    )
    
    db.session.add(pictograma)
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'pictograma': {'id': pictograma.id, 'nome': pictograma.nome}
    }), 201


@main.route('/api/pictogramas/<int:pictograma_id>', methods=['PUT'])
@login_required
def api_atualizar_pictograma(pictograma_id):
    """Atualiza um pictograma"""
    pictograma = Pictograma.query.get_or_404(pictograma_id)
    dados = request.get_json()
    
    if dados.get('nome'):
        pictograma.nome = dados['nome']
    if dados.get('imagem_url'):
        pictograma.imagem_url = dados['imagem_url']
    if dados.get('audio_texto'):
        pictograma.audio_texto = dados['audio_texto']
    if dados.get('categoria_id'):
        pictograma.categoria_id = dados['categoria_id']
    if dados.get('ordem'):
        pictograma.ordem = dados['ordem']
    
    db.session.commit()
    return jsonify({'sucesso': True})


@main.route('/api/pictogramas/<int:pictograma_id>', methods=['DELETE'])
@login_required
def api_excluir_pictograma(pictograma_id):
    """Desativa um pictograma"""
    pictograma = Pictograma.query.get_or_404(pictograma_id)
    pictograma.ativo = False
    db.session.commit()
    return jsonify({'sucesso': True})


# ========== API - SESSÕES ==========

@main.route('/api/sessoes', methods=['GET'])
@login_required
def api_listar_sessoes():
    """Lista todas as sessões"""
    sessoes = Sessao.query.order_by(desc(Sessao.data_inicio)).all()

    return jsonify({
        'sessoes': [{
            'id': s.id,
            'paciente_id': s.paciente_id,
            'paciente_nome': s.paciente.nome,
            'profissional_id': s.profissional_id,
            'profissional_nome': s.profissional.nome if s.profissional else 'N/A',
            'data_inicio': s.data_inicio.isoformat(),
            'data_fim': s.data_fim.isoformat() if s.data_fim else None,
            'duracao_minutos': s.duracao_minutos,
            'duracao': int((s.data_fim - s.data_inicio).total_seconds()) if (s.finalizada and s.data_fim) else None,
            'avaliacao': s.avaliacao,
            'finalizada': s.finalizada,
            'total_interacoes': HistoricoSelecao.query.filter_by(sessao_id=s.id).count()
        } for s in sessoes]
    })


@main.route('/api/sessoes', methods=['POST'])
@login_required
def api_criar_sessao():
    """Inicia nova sessão"""
    dados = request.get_json()
    paciente_id = dados.get('paciente_id')
    
    if not paciente_id:
        return jsonify({'erro': 'paciente_id obrigatório'}), 400
    
    sessao_aberta = Sessao.query.filter_by(paciente_id=paciente_id, finalizada=False).first()
    
    if sessao_aberta:
        return jsonify({
            'sucesso': True,
            'sessao_id': sessao_aberta.id,
            'mensagem': 'Sessão já estava aberta'
        })
    
    sessao = Sessao(
        paciente_id=paciente_id,
        profissional_id=session.get('usuario_id')
    )
    db.session.add(sessao)
    db.session.commit()
    
    return jsonify({'sucesso': True, 'sessao_id': sessao.id}), 201


@main.route('/api/sessoes/<int:sessao_id>/selecao', methods=['POST'])
@login_required
def api_registrar_selecao(sessao_id):
    """Registra seleção de pictograma"""
    dados = request.get_json()
    pictograma_id = dados.get('pictograma_id')
    tempo_resposta = dados.get('tempo_resposta_segundos')
    
    if not pictograma_id:
        return jsonify({'erro': 'pictograma_id obrigatório'}), 400
    
    historico = HistoricoSelecao(
        sessao_id=sessao_id,
        pictograma_id=pictograma_id,
        tempo_resposta_segundos=tempo_resposta
    )
    
    db.session.add(historico)
    db.session.commit()
    
    return jsonify({'sucesso': True, 'historico_id': historico.id}), 201


@main.route('/api/sessoes/<int:sessao_id>/finalizar', methods=['POST'])
@login_required
def api_finalizar_sessao(sessao_id):
    """Finaliza sessão com avaliação obrigatória"""
    sessao = Sessao.query.get_or_404(sessao_id)
    dados = request.get_json() or {}
    
    avaliacao = dados.get('avaliacao', '').strip()
    
    if not avaliacao:
        return jsonify({'erro': 'Avaliação é obrigatória para finalizar a sessão'}), 400
    
    sessao.data_fim = datetime.now()
    sessao.finalizada = True
    sessao.avaliacao = avaliacao
    
    duracao = sessao.data_fim - sessao.data_inicio
    sessao.duracao_minutos = int(duracao.total_seconds() / 60)
    
    if dados.get('observacoes'):
        sessao.observacoes = dados['observacoes']
    
    db.session.commit()
    
    return jsonify({'sucesso': True, 'duracao_minutos': sessao.duracao_minutos})


@main.route('/api/sessoes/<int:sessao_id>/historico', methods=['GET'])
@login_required
def api_obter_historico_sessao(sessao_id):
    """Obtém histórico de uma sessão"""
    sessao = Sessao.query.get_or_404(sessao_id)
    
    historico = HistoricoSelecao.query.filter_by(
        sessao_id=sessao_id
    ).order_by(HistoricoSelecao.timestamp).all()
    
    return jsonify({
        'sessao_id': sessao.id,
        'paciente_nome': sessao.paciente.nome,
        'profissional_nome': sessao.profissional.nome if sessao.profissional else 'N/A',
        'data_inicio': sessao.data_inicio.isoformat(),
        'data_fim': sessao.data_fim.isoformat() if sessao.data_fim else None,
        'duracao_minutos': sessao.duracao_minutos,
        'avaliacao': sessao.avaliacao,
        'finalizada': sessao.finalizada,
        'historico': [{
            'id': h.id,
            'pictograma_nome': h.pictograma.nome,
            'pictograma_imagem': h.pictograma.imagem_url,
            'categoria_nome': h.pictograma.categoria.nome,
            'timestamp': h.timestamp.isoformat(),
            'tempo_resposta_segundos': h.tempo_resposta_segundos
        } for h in historico]
    })


# ========== API - UPLOAD DE IMAGEM ==========

@main.route('/api/upload', methods=['POST'])
@login_required
def api_upload_imagem():
    """Upload de imagem para pictograma via Cloudinary ou local"""
    import os
    from flask import current_app

    if 'imagem' not in request.files:
        return jsonify({'erro': 'Nenhuma imagem enviada'}), 400

    arquivo = request.files['imagem']

    if arquivo.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400

    extensoes_permitidas = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    extensao = arquivo.filename.rsplit('.', 1)[1].lower() if '.' in arquivo.filename else ''

    if extensao not in extensoes_permitidas:
        return jsonify({'erro': 'Formato não permitido'}), 400

    # Verificar se Cloudinary está configurado
    cloudinary_configured = all([
        current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        current_app.config.get('CLOUDINARY_API_KEY'),
        current_app.config.get('CLOUDINARY_API_SECRET')
    ])

    if cloudinary_configured:
        # Usar Cloudinary (produção)
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
                api_key=current_app.config.get('CLOUDINARY_API_KEY'),
                api_secret=current_app.config.get('CLOUDINARY_API_SECRET')
            )

            resultado = cloudinary.uploader.upload(
                arquivo,
                folder='pictogramas_caa',
                resource_type='image',
                transformation=[
                    {'width': 500, 'height': 500, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )

            url = resultado['secure_url']
            return jsonify({'sucesso': True, 'url': url})

        except Exception as e:
            return jsonify({'erro': f'Erro ao fazer upload no Cloudinary: {str(e)}'}), 500
    else:
        # Usar armazenamento local (desenvolvimento)
        try:
            nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{arquivo.filename}"
            pasta_uploads = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'images')
            os.makedirs(pasta_uploads, exist_ok=True)

            caminho_completo = os.path.join(pasta_uploads, nome_arquivo)
            arquivo.save(caminho_completo)

            url = f"/static/images/{nome_arquivo}"
            return jsonify({'sucesso': True, 'url': url})

        except Exception as e:
            return jsonify({'erro': f'Erro ao salvar arquivo localmente: {str(e)}'}), 500


# ========== API - HEALTH CHECK ==========

@main.route('/api/health', methods=['GET'])
def api_health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'versao': '2.0.0',
        'sistema': 'CAA - Instituto Tia Dani'
    })
