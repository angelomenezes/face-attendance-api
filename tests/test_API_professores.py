'''
    Testes para cada endpoint da API
'''

# Professores
from conftest import clear_data
from core.models import Professor

class Test_Professores:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Nenhum professor registrado
        response = client.get('/professores/', headers=headers)

        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 2 - Não existe professor com o ID
        response = client.get('/professores/1/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe professor com esse ID no banco de dados.'

        # CENÁRIO 3 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.commit()

        response = client.get('/professores/', headers=headers)
        assert response.json[0]['nome'] == 'AAA'

        response = client.get('/professores/1/', headers=headers)
        assert response.json[0]['nome'] == 'AAA'

        response = client.get('/professores/?nome=AAA', headers=headers)
        assert response.json[0]['nome'] == 'AAA'

        response = client.get('/professores/?departamento=AAA', headers=headers)
        assert response.json[0]['nome'] == 'AAA'

        response = client.get('/professores/?instituicao=AAA', headers=headers)
        assert response.json[0]['nome'] == 'AAA'

        # CLEAN UP
        clear_data(_db)

    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)

        data = {
            "nome": "Carlos",
            "departamento": "Ciencia da Computacao",
            "instituicao": "UFS"
        }
        
        # CENÁRIO 1 - OK
        response = client.post('/professores/', data=data, headers=headers)
        assert response.status_code == 201
        assert response.json == {'professor.id': 1}

        # CENÁRIO 2 - Professor já registrado
        response = client.post('/professores/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Professor já registrado com essas informações (nome, departamento, instituição) no banco de dados.'
        
        # CLEAN UP
        clear_data(_db)

    def test_put(self, get_client_db):
        # PUT
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.commit()

        data = {
            "nome": "Leonardo"
        }

        response = client.put('/professores/1/', data=data, headers=headers)
        assert response.status_code == 204

        # CENÁRIO 2 - Tentativa de atualizar com ID não presente no banco de dados
        response = client.put('/professores/100/', data=data, headers=headers)
        assert response.json['message'] == 'Não existe professor com esse ID no banco de dados.'

        # CLEAN UP
        clear_data(_db)

    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)
        
        # CENÁRIO 1 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.commit()

        response = client.delete('/professores/1/', headers=headers)
        assert response.status_code == 204

        # CENÁRIO 2 - Tentativa de deletar um ID que não está mais no banco de dados
        response = client.delete('/professores/1/', headers=headers)
        assert response.status_code == 400
        assert response.json['message']  == 'Não existe professor com esse ID no banco de dados.'

        # CLEAN UP
        clear_data(_db)
