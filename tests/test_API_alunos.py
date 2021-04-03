'''
    Testes para cada endpoint da API
'''

# Alunos
from conftest import clear_data
from core.models import Aluno
from core.utils import from_img_dir_to_bytes
import os 

class Teste_Alunos:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Sem alunos registrados
        response = client.get('/alunos/', headers=headers)

        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 2 - Aluno não registrado
        response = client.get('/alunos/101010/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matricula no banco de dados.'

        # CENÁRIO 3 - 1 Aluno registrado
        mock_data = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_data))
        _db.session.commit()

        response = client.get('/alunos/', headers=headers)
        assert response.json[0]['nome'] == 'Ivete'

        response = client.get('/alunos/101010/', headers=headers)
        assert response.json[0]['nome'] == 'Ivete'

        response = client.get('/alunos/?nome=Ivete', headers=headers)
        assert response.json[0]['nome'] == 'Ivete'

        response = client.get('/alunos/?matricula=101010', headers=headers)
        assert response.json[0]['nome'] == 'Ivete'

        response = client.get('/alunos/?curso=Danca', headers=headers)
        assert response.json[0]['nome'] == 'Ivete'

        # CLEAN UP
        clear_data(_db)


    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Tentativa de registro de aluno com imagem sem rosto

        file = os.path.join("./tests/test_images/door.jpg")
        img_file = (file, './tests/test_images/door.jpg')
        data = {
            "nome": "Ivete",
            "curso": "Dança",
            "matricula": "101010",
            "imagem_aluno": img_file
        }

        response = client.post('/alunos/', data=data, content_type='multipart/form-data', headers=headers)
        assert response.status_code == 400 # Já que não existe face na imagem
        assert response.json['message'] == 'Foram detectadas nenhuma ou mais de uma face na imagem enviada.'

        # CENÁRIO 2 - OK
        file = os.path.join("./tests/test_images/ivete.jpg")
        img_file = (file, './tests/test_images/ivete.jpg')

        data = {
            "nome": "Ivete",
            "curso": "Dança",
            "matricula": "101010",
            "imagem_aluno": img_file
        } 

        response = client.post('/alunos/', data=data, content_type='multipart/form-data', headers=headers)

        assert response.status_code == 201
        assert response.json == {'aluno.matricula': '101010'}

        # CENÁRIO 3 - Tentativa de registro novo para uma mesma matrícula
        response = client.post('/alunos/', data=data, content_type='multipart/form-data', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Já existe aluno com essa matrícula.'

        # CLEAN UP
        clear_data(_db)


    def test_put(self, get_client_db):
        # PUT
        client, _db, headers = get_client_db
        clear_data(_db)
        mock_img = from_img_dir_to_bytes('./tests/test_images/door.jpg')
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_img))
        _db.session.commit()

        # CENÁRIO 1 - Tentativa de atualização de aluno que não existe
        response = client.put('/alunos/202020/', headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matricula no banco de dados.'

        # CENÁRIO 2 - Tentativa de atualização de registro de aluno com imagem sem rosto
        file = os.path.join("./tests/test_images/door.jpg")
        img_file = (file, './tests/test_images/door.jpg')
        data = {
            "imagem_aluno": img_file
        }

        response = client.put('/alunos/101010/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Foram detectadas nenhuma ou mais de uma face na imagem enviada.'

        # CENÁRIO 3 - OK
        file = os.path.join("./tests/test_images/claudia.jpg")
        img_file = (file, './tests/test_images/claudia.jpg')

        data = {
            "nome": "Claudia",
            "curso": "Audiovisual",
            "matricula": "303030",
            "imagem_aluno": img_file
        }

        response = client.put('/alunos/101010/', data=data, headers=headers)
        assert response.status_code == 204

        # CLEAN UP
        clear_data(_db)


    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        mock_img = from_img_dir_to_bytes('./tests/test_images/door.jpg')
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_img))
        _db.session.commit()

        response = client.delete('/alunos/101010/', headers=headers)
        assert response.status_code == 204

        # CENÁRIO 2 - Tentativa de deletar aluno que já não existe
        response = client.delete('/alunos/101010/', headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matricula no banco de dados.'
        
        # CLEAN UP
        clear_data(_db)



    