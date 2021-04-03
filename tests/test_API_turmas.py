'''
    Testes para cada endpoint da API
'''

# Turmas
from core.models import Professor, Turma
from conftest import clear_data

class Teste_Turmas:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Não existem turmas registradas ainda
        response = client.get('/turmas/', headers=headers)

        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 2 - Não existe turma com o código indicado
        response = client.get('/turmas/1/', headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 3 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.get('/turmas/', headers=headers)
        assert response.json[0]['nome'] == 'Metodologia Cientifica'

        response = client.get('/turmas/?nome=Metodologia%20Cientifica', headers=headers)
        assert response.json[0]['nome'] == 'Metodologia Cientifica'

        response = client.get('/turmas/?codigo=SCC5900', headers=headers)
        assert response.json[0]['nome'] == 'Metodologia Cientifica'

        response = client.get('/turmas/?semestre=2020.2', headers=headers)
        assert response.json[0]['nome'] == 'Metodologia Cientifica'

        response = client.get('/turmas/?professor_id=1', headers=headers)
        assert response.json[0]['nome'] == 'Metodologia Cientifica'

        response = client.get('/turmas/SCC5900/', headers=headers)
        assert response.json[0]['nome'] == 'Metodologia Cientifica'

        # CLEAN UP
        clear_data(_db)

    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)
        
        data = {
            "nome": "Metodologia Científica",
            "codigo": "SCC5900",
            "semestre": "2021.2",
            "professor_id": 1
        }

        # CENÁRIO 1 - Não existe professor com o ID indicado que irá assumir disciplina
        response = client.post('/turmas/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe professor com esse ID no banco de dados.'

        # CENÁRIO 3 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.commit()        

        response = client.post('/turmas/', data=data, headers=headers)

        assert response.status_code == 201
        assert response.json == {'turma.codigo': 'SCC5900'}

        # CENÁRIO 3 - Tentativa de criar instância de turma com mesmo código
        response = client.post('/turmas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Já existe turma com esse código no banco de dados.'

        # CLEAN UP
        clear_data(_db)


    def test_put(self, get_client_db):
        # PUT
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Tentativa de atualizar turma com código não presente no banco de dados
        data = {
            "nome": "Ciencias Sociais"
        }
        response = client.put('/turmas/SCC5900/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.put('/turmas/SCC5900/', data=data, headers=headers)
        assert response.status_code == 204

        # CENÁRIO 3 - Tentativa de atualizar turma com ID de professor não existente
        data = {
            "professor_id": 100
        }
        response = client.put('/turmas/SCC5900/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe professor com esse ID no banco de dados.'
        
        # CLEAN UP
        clear_data(_db)


    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.delete('/turmas/SCC5900/', headers=headers)
        assert response.status_code == 204

        # CENÁRIO 2 - Tentativa de deletar turma que não existe mais no banco de dados
        response = client.delete('/turmas/SCC5900/', headers=headers)
        assert response.status_code == 400
        assert response.json['message']  == 'Não existe turma com esse codigo no banco de dados.'

        # CLEAN UP
        clear_data(_db)


    