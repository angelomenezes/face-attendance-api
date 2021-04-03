'''
    Testes para cada endpoint da API
'''

# Variaveis do Frontend
from core.models import FrontendVariavel
from conftest import clear_data

class Test_Variaveis_Frontend:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Sem variáveis registradas
        response = client.get('/frontend/', headers=headers)
        
        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 2 - Tentativa de acesso a variável não registrada
        response = client.get('/frontend/1/', headers=headers)
        
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe variável com esse ID'

        # CENÁRIO 3 - OK
        _db.session.add(FrontendVariavel(nome='Width', valor='30em'))
        _db.session.commit()

        response = client.get('/frontend/', headers=headers)
        assert response.json[0]['nome'] == 'Width'

        response = client.get('/frontend/1/', headers=headers)
        assert response.json[0]['nome'] == 'Width'

        response = client.get('/frontend/?nome=Width', headers=headers)
        assert response.json[0]['nome'] == 'Width'

        response = client.get('/frontend/?valor=30em', headers=headers)
        assert response.json[0]['nome'] == 'Width'

        # CLEAN UP
        clear_data(_db)

    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        data = {
            "nome": "Width",
            "valor": "30em",
        }
        
        response = client.post('/frontend/', data=data, headers=headers)
        assert response.status_code == 201
        assert response.json == {'frontend_variavel.id': 1}
        
        # CENÁRIO 2 - Tentativa de registro com variável de mesmo nome
        data = {
            "nome": "Width",
            "valor": "50em",
        }
        
        response = client.post('/frontend/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Já existe variável com esse nome no banco de dados.'

        # CLEAN UP
        clear_data(_db)

    def test_put(self, get_client_db):
        # PUT
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        _db.session.add(FrontendVariavel(nome='Width', valor='30em'))
        _db.session.commit()

        data = {
            'nome': 'Height',
            'valor': '12em'
        }

        response = client.put('/frontend/1/', data=data, headers=headers)
        assert response.status_code == 204

        # CENÁRIO 2 - Tentativa de atualização de variável não registrada
        response = client.put('/frontend/100/', data=data, headers=headers)
        
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe variável com esse ID'

        # CENÁRIO 3 - Tentativa de registro para variável com nome já registrado
        response = client.put('/frontend/1/', data=data, headers=headers)
        
        assert response.status_code == 400
        assert response.json['message'] == 'Já existe variável com esse nome no banco de dados.'

        # CLEAN UP
        clear_data(_db)

    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)
        
        # CENÁRIO 1
        _db.session.add(FrontendVariavel(nome='Width', valor='30em'))
        _db.session.commit()

        response = client.delete('/frontend/1/', headers=headers)
        assert response.status_code == 204

        response = client.delete('/frontend/1/', headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe variável com esse ID'

        # CLEAN UP
        clear_data(_db)
