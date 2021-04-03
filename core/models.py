from config import db, ma
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context

### Models

class Professor(db.Model):
    __tablename__ = 'professor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db. String(50), unique=False, nullable=False)
    departamento = db.Column(db.String(40), nullable=False)
    instituicao = db.Column(db.String(40), nullable=False)
    turmas = db.relationship('Turma', backref='professor', passive_deletes=True)


class Aluno(db.Model):
    __tablename__ = 'aluno'
    nome = db.Column(db.String(50), unique=False, nullable=False)
    matricula = db.Column(db.String(10), unique=True, nullable=False, primary_key=True)
    curso = db.Column(db.String(40), nullable=False)
    embedding = db.Column(db.LargeBinary(), nullable=True)
    disciplinas = db.relationship('Participante', backref='aluno', passive_deletes=True)


class Turma(db.Model):
    __tablename__ = 'turma'
    nome = db.Column(db.String(50), nullable=False)
    codigo = db.Column(db.String(10), unique=True, nullable=False, primary_key=True)
    semestre = db.Column(db.String(10), nullable=False, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id', ondelete='SET NULL'), nullable=True)
    frequencias = db.relationship('Frequencia', backref='turma', passive_deletes=True)
    participante = db.relationship('Participante', backref='turma', passive_deletes=True)   


class Frequencia(db.Model):
    __tablename__ = 'frequencia'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, 
                          default=datetime.utcnow, 
                          onupdate=datetime.utcnow) # Toda frequência é registrada no UTC por critérios de boas práticas. Precisa ser convertida para a determinada timezone somente no display.
    turma_codigo = db.Column(db.String(10), db.ForeignKey('turma.codigo', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    imagem_turma = db.Column(db.LargeBinary(), nullable=True)
    presenca = db.relationship('Presenca', backref='frequencia', passive_deletes=True, lazy=True)
    erros = db.relationship('AnotacaoErros', backref='frequencia', passive_deletes=True, lazy=True)


class Participante(db.Model):
    __tablename__ = 'participante'
    id = db.Column(db.Integer, primary_key=True)
    turma_codigo = db.Column(db.String(10), db.ForeignKey('turma.codigo', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    matricula = db.Column(db.String(10), db.ForeignKey('aluno.matricula', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    presenca = db.relationship('Presenca', backref='participante', passive_deletes=True, lazy=True)


class Presenca(db.Model):
    __tablename__ = 'presenca'
    id = db.Column(db.Integer, primary_key=True)
    frequencia_id = db.Column(db.Integer, db.ForeignKey('frequencia.id', ondelete='CASCADE'))
    participante_id = db.Column(db.Integer, db.ForeignKey('participante.id', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=True)


class AnotacaoErros(db.Model):
    __tablename__ = 'anotacao_erros'
    id = db.Column(db.Integer, primary_key=True)
    frequencia_id = db.Column(db.Integer, db.ForeignKey('frequencia.id', ondelete='CASCADE'))
    falsos_positivos = db.Column(db.Integer, nullable=False)
    falsos_negativos = db.Column(db.Integer, nullable=False)
    

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class FrontendVariavel(db.Model):
    __tablename__ = 'frontend_variavel'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(128), nullable=True)

### Schemas

class ProfessorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Professor
        load_instance = True


class AlunoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Aluno
        load_instance = True


class TurmaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('codigo', 'semestre', 'nome', 'professor_id')


class ParticipanteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'matricula')


class PresencaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('participante_id', 'status')

class FrequenciaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'timestamp')


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'username')


class FrontendVarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'nome', 'valor')


class ErrosSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('frequencia_id', 'falsos_positivos', 'falsos_negativos')