from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
import numpy as np
import io
from flask import abort
from core.models import db, Aluno, AlunoSchema
from core.utils import *

api = Namespace('alunos', description='Operações relacionadas aos alunos', decorators=[token_required()])

aluno_post_parser = api.parser()
aluno_post_parser.add_argument('nome', type=str, required=True, help='Nome do Aluno')
aluno_post_parser.add_argument('matricula', type=str, required=True, help='Matricula do Aluno')
aluno_post_parser.add_argument('curso', type=str, required=True, help='Curso de origem do Aluno na Universidade')
aluno_post_parser.add_argument('imagem_aluno', location='files', type=FileStorage, required=True, help='Imagem do Aluno a ser utilizada para extrair embedding')

aluno_get_parser = api.parser()
aluno_get_parser.add_argument('nome', type=str, help='Nome do Aluno')
aluno_get_parser.add_argument('matricula', type=str, help='Matricula do Aluno')
aluno_get_parser.add_argument('curso', type=str, help='Curso de origem do Aluno na Universidade')


aluno_field = api.model('AlunoField', {
    'nome': fields.String,
    'matricula': fields.String,
    'curso': fields.String
})

@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_todos_alunos(Resource):
    @api.response(200, 'Success', aluno_field)
    @api.expect(aluno_get_parser)
    def get(self):
        '''
        Retorna todos os alunos do banco de dados baseado na query enviada.
        '''
        args = aluno_get_parser.parse_args(strict=True)
        args = clear_parser(args)

        if args:
            alunos = Aluno.query.filter_by(**args).order_by(Aluno.nome)
        else:
            alunos = Aluno.query.order_by(Aluno.matricula).all()

        return AlunoSchema(many=True, only=('nome', 'matricula', 'curso')).dump(alunos)
    
    @api.response(400, 'Já existe aluno com essa matrícula. \n'
                       'Foram detectadas nenhuma ou mais de uma face na imagem enviada.')
    @api.response(201, 'Success', api.model('matricula', {'aluno.matricula': fields.String}))
    @api.expect(aluno_post_parser)
    def post(self):
        '''
        Registra um aluno no banco de dados
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, required=True, help='Nome do Aluno')
        parser.add_argument('matricula', type=str, required=True, help='Matricula do Aluno')
        parser.add_argument('curso', type=str, required=True, help='Curso de origem do Aluno na Universidade')
        parser.add_argument('imagem_aluno', location='files', type=FileStorage, required=True, help='Imagem do Aluno a ser utilizada para extrair embedding.')
        args = parser.parse_args(strict=True)

        if Aluno.query.filter_by(matricula=args.matricula).first():
            abort(400, 'Já existe aluno com essa matrícula.')

        # Processa foto do aluno para pegar o array/embedding de features
        img_bytes = args.imagem_aluno.read()

        face_embedding = np.array(process_faces(img_bytes))

        if len(face_embedding) != 1:
            abort(400, 'Foram detectadas nenhuma ou mais de uma face na imagem enviada.')

        # Obtem o binario desse array
        face_binary = io.BytesIO()
        np.save(face_binary, face_embedding)
        face_binary.seek(0)
        
        aluno_selected = Aluno(nome=args.nome, 
                               matricula=args.matricula, 
                               curso=args.curso, 
                               embedding=face_binary.read())
        
        db.session.add(aluno_selected)
        db.session.commit()

        return {'aluno.matricula': aluno_selected.matricula}, 201


@api.doc(responses={401: 'Token inválida. \n' 
                         'Token já expirou. \n'
                         'O header de autorização não está presente.'})
class rota_acesso_unico_alunos(Resource):
    @api.response(200, 'Success', aluno_field)
    @api.response(400, 'Não existe aluno com essa matrícula no banco de dados.')
    def get(self, matricula):
        '''
        Retorna os dados de um aluno com a determinada matricula presente no banco de dados.
        '''
        aluno_selected = Aluno.query.filter_by(matricula=matricula)

        if not aluno_selected.first():
            return abort(400, 'Não existe aluno com essa matricula no banco de dados.')

        return AlunoSchema(many=True, only=('nome', 'matricula', 'curso')).dump(aluno_selected)


    @api.response(204, 'Success')
    @api.response(400, 'Não existe aluno com essa matrícula no banco de dados. \n'
                       'Foram detectadas nenhuma ou mais de uma face na imagem enviada.')
    @api.expect(aluno_field)
    def put(self, matricula):
        '''
        Atualiza as informações de um aluno com determinada matricula (a sua imagem só pode ser atualizada com envio de 'formData' e não está disponível para teste no envio de JSON pelo body do Swagger).
        '''
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('nome', type=str, help='Nome do Aluno')
        parser.add_argument('matricula', type=str, help='Matricula do Aluno')
        parser.add_argument('curso', type=str, help='Curso de origem do Aluno na Universidade')
        parser.add_argument('imagem_aluno', location='files', type=FileStorage, help='Imagem do Aluno a ser utilizada para extrair embedding.')
        args = parser.parse_args(strict=True)

        aluno_selected = Aluno.query.filter_by(matricula=matricula)

        if not aluno_selected.first():
            return abort(400, 'Não existe aluno com essa matricula no banco de dados.')
        
        if args.nome:
            aluno_selected.update(dict(nome=args.nome))
        
        if args.matricula:
            aluno_selected.update(dict(matricula=args.matricula))
        
        if args.curso:
            aluno_selected.update(dict(curso=args.curso))

        if args.imagem_aluno:
            face_embedding = np.array(process_faces(args.imagem_aluno.read()))
            
            if len(face_embedding) != 1:
                abort(400, 'Foram detectadas nenhuma ou mais de uma face na imagem enviada.')

            face_binary = io.BytesIO()
            np.save(face_binary, face_embedding)
            face_binary.seek(0)
            
            aluno_selected.update(dict(embedding=face_binary.read()))
        
        db.session.commit()

        return {}, 204

    @api.response(400, 'Não existe aluno com essa matrícula no banco de dados.')
    @api.response(204, 'Success')
    def delete(self, matricula):
        '''
        Deleta um aluno com a determinado matricula presente no banco de dados.
        '''
        aluno_selected = Aluno.query.filter_by(matricula=matricula)

        if not aluno_selected.first():
            return abort(400, 'Não existe aluno com essa matricula no banco de dados.')

        aluno_selected.delete()

        db.session.commit()

        return {}, 204


api.add_resource(rota_acesso_todos_alunos, '/')
api.add_resource(rota_acesso_unico_alunos, '/<string:matricula>/')