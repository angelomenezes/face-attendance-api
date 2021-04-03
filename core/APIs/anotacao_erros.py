from flask_restx import Namespace, Resource, fields
from flask import abort
from core.models import *
from core.utils import token_required

api = Namespace('erros', description='Operações para verificação dos registros de erros da API de reconhecimento facial.', decorators=[token_required()])

erros_field = api.model('ErrosField', {
    'frequencia_id': fields.Integer,
    'falsos_positivos': fields.Integer,
    'falsos_negativos': fields.Integer
})

@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_erros(Resource):
    @api.response(400, 'Não existe turma com esse código no banco de dados. \n'
                       'Não existe frequência com esse ID no banco de dados.')
    @api.response(200, 'Success', erros_field)
    def get(self, codigo, frequencia_id):
        '''
        Acesso ao registro de correções feitas através da rota PUT para a presença de alunos
        '''
        if not Turma.query.filter_by(codigo=codigo).first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')
        
        if not Frequencia.query.filter_by(id=frequencia_id).first():
            return abort(400, 'Não existe frequencia com esse ID no banco de dados.')

        erros = AnotacaoErros.query.filter_by(frequencia_id=frequencia_id)
        
        return ErrosSchema(many=True).dump(erros)

api.add_resource(rota_acesso_erros, '/<string:codigo>/frequencias/<int:frequencia_id>/erros/')