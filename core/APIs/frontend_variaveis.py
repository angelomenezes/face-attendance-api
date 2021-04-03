from core.utils import clear_parser
from flask_restx import Namespace, Resource, fields, reqparse
from flask import abort
from core.models import db, FrontendVariavel, FrontendVarSchema
from core.utils import token_required

api = Namespace('frontend', description='Operações para envio de variáveis externas do frontend', decorators=[token_required()])

variavel_get_parser = reqparse.RequestParser(bundle_errors=True)
variavel_get_parser.add_argument('nome', type=str, help='Nome da variavel')
variavel_get_parser.add_argument('valor', type=str, help='Valor em string')

variavel_field = api.model('Variavel', {
    'nome': fields.String,
    'valor': fields.String,
})


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todas_variaveis(Resource):
    @api.response(200, 'Success', variavel_field)
    @api.expect(variavel_get_parser)
    def get(self):
        '''
        Retorna todas as variaveis externas listadas no banco de dados.
        '''
        args = variavel_get_parser.parse_args(strict=True)
        args = clear_parser(args)

        if args:
            var = FrontendVariavel.query.filter_by(**args).order_by(FrontendVariavel.id)
        else:
            var = FrontendVariavel.query.order_by(FrontendVariavel.id).all()

        return FrontendVarSchema(many=True).dump(var)

    @api.response(400, 'Não foram enviadas variáveis válidas para registro no banco de dados \n'
                       'Já existe variável com esse nome no banco de dados.')
    @api.response(201, 'Success', api.model('var.id', {'frontened_variavel.id': fields.Integer}))
    @api.expect(variavel_field)
    def post(self):
        '''
        Registra uma variável externa no banco de dados.
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, required=True, help='Nome da variavel')
        parser.add_argument('valor', type=str, required=True, help='Valor em string')
        args = parser.parse_args(strict=True)

        if FrontendVariavel.query.filter_by(nome=args.nome).first():
            abort(400, 'Já existe variável com esse nome no banco de dados.')

        var_selected = FrontendVariavel(nome=args.nome,
                                        valor=args.valor)

        db.session.add(var_selected)
        db.session.commit()
        db.session.refresh(var_selected)

        return {'frontend_variavel.id': var_selected.id}, 201


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_unico_variaveis(Resource):
    @api.response(400, 'Não existe variável com esse ID')
    @api.response(200, 'Success', variavel_field)
    def get(self, id):
        '''
        Retorna uma variavel externa com base em seu ID.
        '''
        var = FrontendVariavel.query.filter_by(id=id)

        if not var.first():
            return abort(400, 'Não existe variável com esse ID')
 
        return FrontendVarSchema(many=True).dump(var)

    @api.response(204, 'Success')
    @api.response(400, 'Não existe variável com esse ID. \n'
                       'Já existe variável com esse nome no banco de dados.')
    @api.expect(variavel_field)
    def put(self, id):
        '''
        Atualiza uma variavel externa com base em seu ID.
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, help='Nome da variavel')
        parser.add_argument('valor', type=str, help='Valor em string')
        args = parser.parse_args(strict=True)

        var = FrontendVariavel.query.filter_by(id=id)

        if not var.first():
            return abort(400, 'Não existe variável com esse ID')

        if args.nome:
            if FrontendVariavel.query.filter_by(nome=args.nome).first():
                abort(400, 'Já existe variável com esse nome no banco de dados.')
            var.update(dict(nome=args.nome))

        if args.valor:
            var.update(dict(valor=args.valor))

        db.session.commit()

        return {}, 204
    
    @api.response(204, 'Success')
    @api.response(400, 'Não existe variável com esse ID.')
    def delete(self, id):
        '''
        Deleta uma variável externa do banco de dados pelo ID.
        '''
        var = FrontendVariavel.query.filter_by(id=id)

        if not var.first():
            return abort(400, 'Não existe variável com esse ID')

        var.delete()

        db.session.commit()

        return {}, 204

api.add_resource(rota_acesso_todas_variaveis, '/')
api.add_resource(rota_acesso_unico_variaveis, '/<int:id>/')
