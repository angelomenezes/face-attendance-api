from core.utils import clear_parser, token_required
from flask_restx import Namespace, Resource, fields, reqparse
from flask import abort
from core.models import db, Professor, ProfessorSchema
from core.utils import token_required

api = Namespace('professores', description='Operações relacionadas aos professores', decorators=[token_required()])

professor_get_parser = reqparse.RequestParser(bundle_errors=True)
professor_get_parser.add_argument('nome', type=str, help='Nome do professor')
professor_get_parser.add_argument('departamento', type=str, help='Nome do departamento')
professor_get_parser.add_argument('instituicao', type=str, help='Instituicao de ensino')
        
professor_field_input = api.model('ProfessorInput', {
    'nome': fields.String,
    'departamento': fields.String,
    'instituicao': fields.String
})

professor_field_output = api.model('ProfessorOutput', {
    'id': fields.Integer,
    'nome': fields.String,
    'departamento': fields.String,
    'instituicao': fields.String
})
@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todos_professores(Resource):
    @api.response(200, 'Success', professor_field_output)
    @api.expect(professor_get_parser)
    @token_required()
    def get(self):
        '''
        Retorna todos os professores no banco de dados com base na query.
        '''
        args = professor_get_parser.parse_args(strict=True)
        args = clear_parser(args)

        if args:
            professores = Professor.query.filter_by(**args)
        else:
            professores = Professor.query.order_by(Professor.id).all()

        return ProfessorSchema(many=True).dump(professores)

    @api.response(201, 'Success', api.model('ProfessorID', {'professor.id': fields.Integer}))
    @api.response(400, 'Professor já registrado com essas informações (nome, departamento, instituição) no banco de dados.')
    @api.expect(professor_field_input)
    def post(self):
        '''
        Registra um professor no banco de dados.
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, required=True, help='Nome do professor')
        parser.add_argument('departamento', type=str, required=True, help='Nome do departamento')
        parser.add_argument('instituicao', type=str, required=True, help='Instituicao de ensino')
        args = parser.parse_args(strict=True)

        professor_selected = Professor.query.filter_by(**args)

        if professor_selected.first():
            return abort(400, 'Professor já registrado com essas informações (nome, departamento, instituição) no banco de dados.')

        professor_selected = Professor(**args)
        
        db.session.add(professor_selected)
        db.session.commit()
        db.session.refresh(professor_selected) # Para obter o ID de registro.

        return {'professor.id': professor_selected.id}, 201


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_unico_professores(Resource):
    @api.response(200, 'Success', professor_field_output)
    @api.response(400, 'Não existe professor com esse ID no banco de dados.')
    def get(self, unique_id):
        '''
        Retorna os dados de um professor com o determinado ID presente no banco de dados.
        '''
        professor_selected = Professor.query.filter_by(id=unique_id)

        if not professor_selected.first():
            return abort(400, 'Não existe professor com esse ID no banco de dados.')

        return ProfessorSchema(many=True).dump(professor_selected)

    @api.response(204, 'Success')
    @api.response(400, 'Não existe professor com esse ID no banco de dados.')
    @api.expect(professor_field_input)
    def put(self, unique_id):
        '''
        Atualiza as informações de um professor com o determinado ID presente no banco de dados.
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, help='Nome do professor')
        parser.add_argument('departamento', type=str, help='Nome do departamento')
        parser.add_argument('instituicao', type=str, help='Instituicao de ensino')
        args = parser.parse_args(strict=True)
        args = clear_parser(args)

        professor_selected = Professor.query.filter_by(id=unique_id)

        if not professor_selected.first():
            return abort(400, 'Não existe professor com esse ID no banco de dados.')
                
        if args:
            professor_selected.update(dict(**args))    
            db.session.commit()

        return {}, 204

    @api.response(400, 'Não existe professor com esse ID no banco de dados.')
    @api.response(204, 'Success')
    def delete(self, unique_id):
        '''
        Deleta um professor com o determinado ID presente no banco de dados.
        '''

        professor_selected = Professor.query.filter_by(id=unique_id)

        if not professor_selected.first():
            return abort(400, 'Não existe professor com esse ID no banco de dados.')

        professor_selected.delete()

        db.session.commit()

        return {}, 204


api.add_resource(rota_acesso_todos_professores, '/')
api.add_resource(rota_acesso_unico_professores, '/<int:unique_id>/')