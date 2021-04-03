from flask_restx import Namespace, Resource, fields, reqparse
from flask import abort
from core.models import *
from core.utils import *

api = Namespace('turmas', description='Operações relacionadas as turmas', decorators=[token_required()])

turma_get_parser = reqparse.RequestParser(bundle_errors=True)
turma_get_parser.add_argument('nome', type=str, help='Nome da disciplina')
turma_get_parser.add_argument('codigo', type=str, help='Codigo da disciplina a ser atualizado')
turma_get_parser.add_argument('semestre', type=str, help='Semestre de oferta da disciplina')
turma_get_parser.add_argument('professor_id', type=int, help='ID do professor que ministra a disciplina')

turma_field = api.model('TurmaField', {
    'nome': fields.String,
    'codigo': fields.String,
    'semestre': fields.String,
    'professor_id': fields.Integer
})


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todas_turmas(Resource):
    @api.response(200, 'Success', turma_field)
    @api.expect(turma_get_parser)
    def get(self):
        '''
        Retorna todas as turmas presentes no banco de dados com base na query.
        '''
        args = turma_get_parser.parse_args(strict=True)
        args = clear_parser(args)

        if args:
            turmas = Turma.query.filter_by(**args)
        else:
            turmas = Turma.query.order_by(Turma.nome).all()
        
        return TurmaSchema(many=True).dump(turmas)

    @api.response(400, 'Já existe turma com esse código no banco de dados. \n'
                       'Não existe professor com esse ID no banco de dados.')
    @api.response(201, 'Success', api.model('TurmaCodigo', {'turma.codigo': fields.String}))
    @api.expect(turma_field)
    def post(self):
        '''
        Registra uma turma no banco de dados.
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, required=True, help='Nome da disciplina')
        parser.add_argument('codigo', type=str, required=True, help='Codigo da disciplina')
        parser.add_argument('semestre', type=str, required=True, help='Semestre de oferta da disciplina')
        parser.add_argument('professor_id', type=int, required=True, help='ID do professor que ministra a disciplina')
        args = parser.parse_args(strict=True)

        if Turma.query.filter_by(codigo=args.codigo).first():
            abort(400, 'Já existe turma com esse código no banco de dados.')

        if not Professor.query.filter_by(id=args.professor_id).first():
            return abort(400, 'Não existe professor com esse ID no banco de dados.')

        turma_selected = Turma(**args)
        
        db.session.add(turma_selected)
        db.session.commit()

        return {'turma.codigo': turma_selected.codigo}, 201 


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_unico_turmas(Resource):
    @api.response(400, 'Não existe turma com esse codigo no banco de dados.')
    @api.response(200, 'Success', turma_field)
    def get(self, codigo):
        '''
        Retorna os dados de uma turma com o determinado código presente no banco de dados.
        '''
        turma_selected = Turma.query.filter_by(codigo=codigo)

        if not turma_selected.first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        return TurmaSchema(many=True).dump(turma_selected)

    @api.response(400, 'Não existe turma com esse código no banco de dados. \n'
                       'Não existe professor com esse ID no banco de dados.')
    @api.response(204, 'Success')
    @api.expect(turma_field)
    def put(self, codigo):
        '''
        Atualiza as informações de uma turma com o determinado código no banco de dados.
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, help='Nome da disciplina')
        parser.add_argument('codigo', type=str, help='Codigo da disciplina a ser atualizado')
        parser.add_argument('semestre', type=str, help='Semestre de oferta da disciplina')
        parser.add_argument('professor_id', type=int, help='ID do professor que ministra a disciplina')
        args = parser.parse_args(strict=True)
        args = clear_parser(args)

        turma_selected = Turma.query.filter_by(codigo=codigo)

        if not turma_selected.first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        if 'professor_id' in args.keys():
            if not Professor.query.filter_by(id=args['professor_id']).first():
                return abort(400, 'Não existe professor com esse ID no banco de dados.')
            
        if args:
            turma_selected.update(dict(**args))
            db.session.commit()
        
        return {}, 204

    @api.response(400, 'Não existe turma com esse código no banco de dados.')
    @api.response(204, 'Success')
    def delete(self, codigo):
        '''
        Deleta uma turma com o determinado codigo presente no banco de dados. 
        '''
        turma_selected = Turma.query.filter_by(codigo=codigo)

        if not turma_selected.first():
            return abort(400, 'Não existe turma com esse codigo no banco de dados.')

        turma_selected.delete()

        db.session.commit()

        return {}, 204


api.add_resource(rota_acesso_todas_turmas, '/')
api.add_resource(rota_acesso_unico_turmas, '/<string:codigo>/')
