from flask_restx import Namespace, Resource, fields, reqparse
from flask import abort
from core.models import *
from core.utils import *

api = Namespace('participantes', description='Operações relacionadas ao registro de alunos participantes das turmas', decorators=[token_required()])

participantes_field = api.model('ParticipantesField', {
    'id': fields.Integer,
    'matricula': fields.String,
})

participante_get_parser = reqparse.RequestParser()
participante_get_parser.add_argument('matricula', type=str, help='Matricula do Aluno')


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todos_participantes(Resource):

    @api.response(400, 'Não existe turma com esse codigo no banco de dados.')
    @api.response(200, 'Success', participantes_field)
    @api.expect(participante_get_parser)
    def get(self, codigo):
        '''
        Retorna os dados dos participantes de uma turma com determinado código presente no banco de dados.
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')
        
        args = participante_get_parser.parse_args()

        if args.matricula is not None:
            alunos_participantes = Participante.query.filter_by(turma_codigo=codigo, matricula=args.matricula)
        else:
            alunos_participantes = Participante.query.filter_by(turma_codigo=codigo).order_by(Participante.id)

        return ParticipanteSchema(many=True).dump(alunos_participantes)

    @api.response(400, 'Não existe turma com esse codigo no banco de dados. \n'
                       'Não existe aluno com essa matrícula no banco de dados.'
                       'Esse aluno já foi registrado nessa disciplina.')
    @api.response(201, 'Success', api.model('participante.id', {'participante.id': fields.Integer}))
    @api.expect(api.model('participante.matricula', {'matricula': fields.Integer}))
    def post(self, codigo):
        '''
        Registra um aluno com determinada matrícula como participante da turma com determinado código no banco de dados.
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=str, required=True, help='Matricula do Aluno')
        args = parser.parse_args(strict=True)

        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        if not Aluno.query.filter_by(matricula=args.matricula).first():
            return abort(400, 'Não existe aluno com essa matrícula no banco de dados.')
        
        if Participante.query.filter_by(turma_codigo=codigo, matricula=args.matricula).first():
            return abort(400, 'Esse aluno já foi registrado nessa disciplina.')

        aluno_participante = Participante(matricula=args.matricula, turma_codigo=codigo)

        db.session.add(aluno_participante)
        db.session.commit()
        db.session.refresh(aluno_participante)
        
        return {'participante.id': aluno_participante.id}, 201


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_unico_participantes(Resource):
    @api.response(400, 'Não existe turma com esse codigo no banco de dados. \n'
                       'Não existe participante com esse ID no banco de dados.')
    @api.response(200, 'Success', 'AlunoField')
    def get(self, codigo, unique_id):
        '''
        Retorna os dados de um aluno participante com determinado ID
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')
        
        aluno_participante = Participante.query.filter_by(turma_codigo=codigo, id=unique_id)

        if not aluno_participante.first():
            return abort(400, 'Não existe participante com esse ID no banco de dados dessa turma.')
        
        return obter_aluno_pela_matricula([aluno_participante.all()[0].matricula])

    @api.response(400, 'Não existe turma com esse codigo no banco de dados. \n'
                       'Não existe participante com esse ID no banco de dados.')
    @api.response(204, 'Success')
    def delete(self, codigo, unique_id):
        '''
        Deleta o registro de um aluno participante com determinada matrícula
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')
        
        aluno_participante = Participante.query.filter_by(turma_codigo=codigo, id=unique_id)

        if not aluno_participante.first():
            return abort(400, 'Não existe participante com esse ID no banco de dados dessa turma.')

        aluno_participante.delete()

        db.session.commit()

        return {}, 204

api.add_resource(rota_acesso_todos_participantes, '/<string:codigo>/participantes/')
api.add_resource(rota_acesso_unico_participantes, '/<string:codigo>/participantes/<int:unique_id>/')
