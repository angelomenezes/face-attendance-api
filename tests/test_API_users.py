'''
    Testes para cada endpoint da API
'''

# Users and Authentication
from core.models import User
from conftest import clear_data

class Teste_Users:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Nenhum usuário cadastrado
        response = client.get('/auth/users/', headers=headers)
        
        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 2 - OK
        user = User(username='Arlindo')
        user.hash_password('Senha')
        _db.session.add(user)
        _db.session.commit()

        response = client.get('/auth/users/', headers=headers)
        assert response.json[0]['username'] == 'Arlindo'

        # CLEAN UP
        clear_data(_db)

    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        data = {
            "username": "Arlindo",
            "password": "Senha"
        }

        response = client.post('/auth/users/', data=data, headers=headers)
        assert response.status_code == 201
        assert response.json == {'username': 'Arlindo'}

        # CENÁRIO 2 - Tentativa de adicionar uma instância com mesmo username
        response = client.post('/auth/users/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Já existe usuário com esse username.'
        
        # CLEAN UP
        clear_data(_db)

    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        user = User(username='Arlindo')
        user.hash_password('Senha')
        _db.session.add(user)
        _db.session.commit()
        
        data = {
            "username": "Arlindo"
        }
        
        response = client.delete('/auth/users/', data=data, headers=headers)
        assert response.status_code == 204

        # CENÁRIO 2 - Tentativa de deletar usuário não mais presente no banco de dados
        response = client.delete('/auth/users/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe usuário com esse username.'

        # CLEAN UP
        clear_data(_db)


class Teste_Login:
    def test_post(self, get_client_db):
        # POST
        client, _db, _ = get_client_db # Para login, não é necessário enviar header de autenticação
        clear_data(_db)

        # CENÁRIO 1 - OK
        user = User(username='Arlindo')
        user.hash_password('Senha')
        _db.session.add(user)
        _db.session.commit()

        data = {
            "username": "Arlindo",
            "password": "Senha"
        }

        response = client.post('/auth/login/', data=data)
        assert response.status_code == 200
        key, _ = list(response.json.items())[0]
        assert key == 'token'

        # CENÁRIO 2 - Tentativa de login com usuário não cadastrado
        data = {
            "username": "Catatau",
            "password": "Senha"
        }

        response = client.post('/auth/login/', data=data)
        assert response.status_code == 401
        assert response.json['message'] == 'Username ou senha inválido'
        
        # CLEAN UP
        clear_data(_db)
