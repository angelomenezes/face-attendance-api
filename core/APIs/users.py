from flask_restx import Namespace, Resource, fields, reqparse
from flask import abort, g
from flask_jwt_extended import create_access_token
from core.models import db, User, UserSchema
import datetime
from core.utils import token_required

api = Namespace('auth', description='Operações relacionadas a autenticação')

user_field_input = api.model('UserInput', {
    'username': fields.String,
    'password': fields.String,
})

user_field_output = api.model('UserOutput', {
    'id': fields.Integer,
    'username': fields.String,
})

username_field = api.model('username', {
    'username': fields.String
})

token_field = api.model('token', {
    'token': fields.String
})


def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    #g.user_id = user.id
    return True


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_geral_usuarios(Resource):
    @api.response(200, 'Success', user_field_output)
    @token_required()
    def get(self):
        '''
        Obtem o username dos usuários registrados na API
        '''
        users = User.query.order_by(User.username).all()
        return UserSchema(many=True).dump(users)

    @api.response(201, 'Success', username_field)
    @api.response(400, 'Já existe usuário com esse username.')
    @api.expect(user_field_input)
    @token_required()
    def post(self):
        '''
        Registra um novo usuário para ter acesso a API
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True, help='Nome do usuário para login')
        parser.add_argument('password', type=str, required=True, help='Senha do usuário')
        args = parser.parse_args(strict=True)
        
        if User.query.filter_by(username = args.username).first() is not None:
            abort(400, 'Já existe usuário com esse username.')
        
        user = User(username=args.username)
        user.hash_password(args.password)

        db.session.add(user)
        db.session.commit()

        return {'username': args.username}, 201

    @api.response(400, 'Não existe usuário com esse username.')
    @api.doc(params={'username': 'Nome do usuário'})
    @token_required()
    def delete(self):
        '''
        Deleta um usuário pelo username do banco de dados.
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Nome do usuário')
        args = parser.parse_args(strict=True)

        user_selected = User.query.filter_by(username = args.username)
        
        if not user_selected.first():
            abort(400, 'Não existe usuário com esse username.')
            
        user_selected.delete()

        db.session.commit()

        return {}, 204

class rota_login(Resource):
    @api.doc(security=None)
    @api.expect(user_field_input)
    @api.response(401, 'Username ou senha inválido')
    @api.response(200, 'Success', token_field)
    def post(self):
        '''
        Realize o acesso de um usuário e gera um token que autoriza acesso aos endpoints da API
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True, help='Nome do usuário para login')
        parser.add_argument('password', type=str, required=True, help='Senha do usuário')
        args = parser.parse_args(strict=True)
        
        autorizado = verify_password(args.username, args.password)

        if not autorizado:
            abort(401, 'Username ou senha inválido')

        user_id = User.query.filter_by(username=args.username).all()[0].id
        
        expires = datetime.timedelta(days=30)
        access_token = create_access_token(identity=str(user_id), expires_delta=expires)

        return {'token': access_token}, 200

api.add_resource(rota_acesso_geral_usuarios, '/users/')
api.add_resource(rota_login, '/login/')