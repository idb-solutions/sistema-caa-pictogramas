from datetime import datetime
from app import db

class Usuario(db.Model):
    """
    Modelo de Usuário (Profissional/Terapeuta)
    Login: username + senha numérica
    """
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)  # Login único
    senha = db.Column(db.String(20), nullable=False)  # Senha numérica simples
    cargo = db.Column(db.String(50))  # Ex: Terapeuta, Fonoaudiólogo, etc.
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pacientes = db.relationship('Paciente', backref='profissional', lazy=True)
    sessoes = db.relationship('Sessao', backref='profissional', lazy=True)

class Paciente(db.Model):
    __tablename__ = 'paciente'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date)
    diagnostico = db.Column(db.Text)
    nivel_suporte = db.Column(db.String(50))
    preferencias = db.Column(db.Text)
    foto_perfil = db.Column(db.String(200))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    sessoes = db.relationship('Sessao', backref='paciente', lazy=True, cascade='all, delete-orphan')

class Categoria(db.Model):
    __tablename__ = 'categoria'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    cor = db.Column(db.String(7))
    icone = db.Column(db.String(50))
    ordem = db.Column(db.Integer)
    
    pictogramas = db.relationship('Pictograma', backref='categoria', lazy=True)

class Pictograma(db.Model):
    __tablename__ = 'pictograma'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    imagem_url = db.Column(db.String(200))
    audio_texto = db.Column(db.String(200))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    ordem = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)
    
    historico = db.relationship('HistoricoSelecao', backref='pictograma', lazy=True)

class Sessao(db.Model):
    """
    Modelo de Sessão de Terapia
    Inclui profissional responsável e avaliação obrigatória
    """
    __tablename__ = 'sessao'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Quem aplicou
    data_inicio = db.Column(db.DateTime, default=datetime.now)
    data_fim = db.Column(db.DateTime)
    duracao_minutos = db.Column(db.Integer)
    observacoes = db.Column(db.Text)
    avaliacao = db.Column(db.Text)  # Avaliação obrigatória ao finalizar
    finalizada = db.Column(db.Boolean, default=False)
    
    historico = db.relationship('HistoricoSelecao', backref='sessao', lazy=True, cascade='all, delete-orphan')

class HistoricoSelecao(db.Model):
    __tablename__ = 'historico_selecao'
    
    id = db.Column(db.Integer, primary_key=True)
    sessao_id = db.Column(db.Integer, db.ForeignKey('sessao.id'), nullable=False)
    pictograma_id = db.Column(db.Integer, db.ForeignKey('pictograma.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    tempo_resposta_segundos = db.Column(db.Float)

class Configuracao(db.Model):
    __tablename__ = 'configuracao'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    descricao = db.Column(db.String(200))