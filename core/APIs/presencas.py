from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask import abort
from core.models import *
from core.utils import *

api = Namespace('presencas', description='Operações relacionadas ao registro de presenca dos alunos', decorators=[token_required()])

presenca_get_parser = reqparse.RequestParser()
presenca_get_parser.add_argument('matricula', type=str, help='Matricula do Aluno')
presenca_get_parser.add_argument('participante_id', type=int, help='ID do Participante da Turma')

presenca_out_field = api.model('PresencaOut', {
    'participante_id': fields.Integer,
    'matricula': fields.String,
    'status': fields.Boolean
})

presenca_body_field = api.model('PresencaOut', {
    'matricula': fields.String(required=True),
    'status': fields.Boolean(required=True)
})


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todos_alunos_status(Resource):
    @api.response(400, 'Não existe turma com esse código no banco de dados. \n'
                       'Não existe frequência com esse ID no banco de dados.')
    @api.response(200, 'Success', presenca_out_field)
    @api.expect(presenca_get_parser)
    def get(self, codigo, frequencia_id):
        '''
        Retorna o status de cada aluno participante da disciplina no determinado dia
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')
        
        if not Frequencia.query.filter_by(id=frequencia_id).first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')

        args = presenca_get_parser.parse_args(strict=True)
        
        if args.matricula is not None:
            id_participante = Participante.query.filter_by(matricula=args.matricula).all()[0].id
            alunos_status = PresencaSchema(many=True).dump(Presenca.query.filter_by(frequencia_id=frequencia_id, participante_id=id_participante))
        
        elif args.participante_id is not None:
            alunos_status = PresencaSchema(many=True).dump(Presenca.query.filter_by(frequencia_id=frequencia_id, participante_id=args.participante_id))

        else:
            alunos_status = PresencaSchema(many=True).dump(Presenca.query.filter_by(frequencia_id=frequencia_id))

        # Gambiarra para adicionar matrícula ao output
        for aluno in alunos_status:
            aluno['matricula'] = Participante.query.filter_by(id=aluno['participante_id']).all()[0].matricula
        
        return alunos_status

    @api.response(400, 'Não existe turma com esse código no banco de dados. \n'
                       'Não existe frequência com esse ID no banco de dados. \n'
                       'Não existe aluno com essa matricula participando da disciplina no banco de dados. \n'
                       'Registro de presença desse aluno já está presente no banco de dados.')
    @api.response(201, 'Success', api.model('participante_id', {'participante.id': fields.Integer}))
    @api.expect(presenca_body_field)
    def post(self, codigo, frequencia_id):
        '''
        Inclui o registro de um aluno com determinada matrícula em determinado dia
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=str, required=True, help='Matricula do Aluno')
        parser.add_argument('status', type=inputs.boolean, required=True, help='Status de presença do aluno')
        args = parser.parse_args(strict=True)

        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        if not Frequencia.query.filter_by(id=frequencia_id).first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')

        aluno_participante = Participante.query.filter_by(turma_codigo=codigo, matricula=args.matricula)

        if not aluno_participante.first():
            return abort(400, 'Não existe aluno com essa matricula participando da disciplina no banco de dados.')

        if Presenca.query.filter_by(frequencia_id=frequencia_id, participante_id=aluno_participante.all()[0].id).first():
            abort(400, 'Registro de presença desse aluno já está presente no banco de dados.')
        
        aluno_status = Presenca(frequencia_id=frequencia_id, participante_id=aluno_participante.all()[0].id, status=args.status)

        db.session.add(aluno_status)
        db.session.commit()

        return {'participante.id': aluno_participante.all()[0].id}, 201


    @api.response(400, 'Não existe turma com esse código no banco de dados. \n'
                       'Não existe frequência com esse ID no banco de dados. \n'
                       'Não existe aluno com essa matricula participando da disciplina no banco de dados. \n'
                       'Aluno não possui presença registrada nesse dia no banco de dados.')
    @api.response(204, 'Success')
    @api.expect(presenca_body_field)
    def put(self, codigo, frequencia_id):
        '''
        Altera o registro de um aluno com determinada matrícula em determinado dia
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=str, required=True, help='Matricula do Aluno')
        parser.add_argument('status', type=inputs.boolean, required=True, help='Status de presença do aluno')
        args = parser.parse_args(strict=True)

        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        if not Frequencia.query.filter_by(id=frequencia_id).first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')

        aluno_participante = Participante.query.filter_by(turma_codigo=codigo, matricula=args.matricula)

        if not aluno_participante.first():
            return abort(400, 'Não existe aluno com essa matricula participando da disciplina no banco de dados.')

        registro_aluno = Presenca.query.filter_by(frequencia_id=frequencia_id, participante_id=aluno_participante.all()[0].id)

        if not registro_aluno.first():
            abort(400, 'Aluno não possui presença registrada nesse dia no banco de dados.')
        
        if registro_aluno.first().status == True and args.status == False: # Modelo cometeu um erro de falso positivo (aferiu presença de quem não estava presente)
            anotacao_erros = AnotacaoErros.query.filter_by(frequencia_id=frequencia_id)
            anotacao_erros.update(dict(falsos_positivos=anotacao_erros.first().falsos_positivos + 1))

        if registro_aluno.first().status == False and args.status == True: # Modelo cometeu um erro de falso negativo (disse que uma pessoa que está presente faltou)
            anotacao_erros = AnotacaoErros.query.filter_by(frequencia_id=frequencia_id)
            anotacao_erros.update(dict(falsos_negativos=anotacao_erros.first().falsos_negativos + 1))

        registro_aluno.update(dict(status=args.status))

        db.session.commit()

        return {}, 204


    @api.response(400, 'Não existe turma com esse código no banco de dados. \n'
                       'Não existe frequência com esse ID no banco de dados. \n'
                       'Não existe aluno com essa matricula participando da disciplina no banco de dados.')
    @api.response(204, 'Success')
    def delete(self, codigo, frequencia_id):
        '''
        Deleta o registro de presença de um aluno com determinada matrícula em certo dia
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('matricula', type=str, required=True, help='Matricula do Aluno')
        args = parser.parse_args(strict=True)

        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        if not Frequencia.query.filter_by(id=frequencia_id).first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')
        
        aluno_participante = Participante.query.filter_by(turma_codigo=codigo, matricula=args.matricula)

        if not aluno_participante.first():
            return abort(400, 'Não existe aluno com essa matricula participando da disciplina no banco de dados.')

        Presenca.query.filter_by(frequencia_id=frequencia_id, participante_id=aluno_participante.all()[0].id).delete()
        db.session.commit()

        return {}, 204

api.add_resource(rota_acesso_todos_alunos_status, '/<string:codigo>/frequencias/<int:frequencia_id>/presencas/')