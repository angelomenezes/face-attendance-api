from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from flask import abort
from core.models import *
from core.utils import *

api = Namespace('frequencias', description='Operações relacionadas ao registro da frequência', decorators=[token_required()])

frequencia_field = api.model('FrequenciaField', {
    'id': fields.Integer,
    'timestamp': fields.DateTime,
})

frequencia_post_parser = reqparse.RequestParser()
frequencia_post_parser.add_argument('imagem_turma', location='files', type=FileStorage, required=True, help='Imagem da turma')

@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todas_frequencias(Resource):
    @api.response(400, 'Não existe turma com esse codigo no banco de dados.')
    @api.response(200, 'Success', frequencia_field)
    def get(self, codigo):
        '''
        Retorna todas as frequencias registradas para determinada turma.
        '''
        turma_selected = Turma.query.filter_by(codigo=codigo)

        if not turma_selected.first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        frequencias_disponiveis = Frequencia.query.filter_by(turma_codigo=codigo).order_by(Frequencia.id)

        return FrequenciaSchema(many=True).dump(frequencias_disponiveis)

    @api.response(400, 'Não existe turma com esse codigo no banco de dados. \n'
                       'Não existem participantes registrados na turma. \n' 
                       'Não foram detectadas faces na imagem enviada.')
    @api.response(201, 'Success', api.model('frequencia.id', {'frequencia.id': fields.Integer}))
    @api.expect(frequencia_post_parser)
    def post(self, codigo):
        '''
        Registra uma frequencia de alunos para determinada turma no banco de dados.
        '''
        args = frequencia_post_parser.parse_args(strict=True)

        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        if not Participante.query.filter_by(turma_codigo=codigo).first():
            return abort(400, 'Não existem participantes registrados na turma.')

        img_bytes = args.imagem_turma.read()

        alunos_presenca_status = checar_presenca_da_turma(turma_codigo=codigo, img_turma=img_bytes)

        frequencia_do_dia = Frequencia(turma_codigo=codigo, imagem_turma=resize_img_bytes(img_bytes))
        
        db.session.add(frequencia_do_dia)
        db.session.commit()
        db.session.refresh(frequencia_do_dia)

        for matricula in alunos_presenca_status.keys():
            participante_id = Participante.query.filter_by(turma_codigo=codigo, matricula=matricula).all()[0].id
            presenca = Presenca(frequencia_id=frequencia_do_dia.id, participante_id=participante_id, status=alunos_presenca_status[matricula])
            db.session.add(presenca)
        
        db.session.add(AnotacaoErros(frequencia_id=frequencia_do_dia.id, falsos_positivos=0, falsos_negativos=0)) # Criando instância para registro dos erros das frequências
        db.session.commit()

        return {'frequencia.id': frequencia_do_dia.id}, 201


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_unico_frequencias(Resource):

    @api.response(400, 'Não existe turma com esse codigo no banco de dados. \n'
                       'Não existe frequencia com esse ID no banco de dados. \n' 
                       'Não foram detectadas faces na imagem enviada.')
    @api.response(204, 'Success')
    @api.expect(frequencia_post_parser)
    def put(self, codigo, frequencia_id):
        '''
        Atualiza uma frequencia já registrada com determinado ID para uma turma no banco de dados.
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        frequencia_selected = Frequencia.query.filter_by(id=frequencia_id)

        if not frequencia_selected.first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')

        parser = reqparse.RequestParser()
        parser.add_argument('imagem_turma', location='files', type=FileStorage, required=True, help='Imagem da turma')
        args = parser.parse_args(strict=True)

        img_bytes = args.imagem_turma.read()
        
        alunos_presenca_status = checar_presenca_da_turma(turma_codigo=codigo, img_turma=img_bytes)
        
        frequencia_selected.update(dict(imagem_turma=resize_img_bytes(img_bytes)))

        # Novo registro de presença
        Presenca.query.filter_by(frequencia_id=frequencia_selected.all()[0].id).delete()
        for matricula in alunos_presenca_status.keys():
            participante_id = Participante.query.filter_by(turma_codigo=codigo, matricula=matricula).all()[0].id
            presenca = Presenca(frequencia_id=frequencia_selected.all()[0].id, participante_id=participante_id, status=alunos_presenca_status[matricula])
            db.session.add(presenca)
        
        # Inicializando nova contagem de erros
        AnotacaoErros.query.filter_by(frequencia_id=frequencia_selected.all()[0].id).delete()
        db.session.add(AnotacaoErros(frequencia_id=frequencia_selected.all()[0].id, falsos_positivos=0, falsos_negativos=0)) # Criando instância para registro dos erros das frequências

        db.session.commit()

        return {}, 204

    @api.response(400, 'Não existe turma com esse codigo no banco de dados. \n'
                       'Não existe frequencia com esse ID no banco de dados.')
    @api.response(204, 'Success')
    def delete(self, codigo, frequencia_id):
        '''
        Deleta o registro de uma frequencia com determinado ID
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        frequencia_selected = Frequencia.query.filter_by(id=frequencia_id)

        if not frequencia_selected.first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')

        frequencia_selected.delete()

        db.session.commit()
        
        return {}, 204


api.add_resource(rota_acesso_todas_frequencias, '/<string:codigo>/frequencias/')
api.add_resource(rota_acesso_unico_frequencias, '/<string:codigo>/frequencias/<int:frequencia_id>/')
