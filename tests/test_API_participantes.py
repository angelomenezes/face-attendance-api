'''
    Testes para cada endpoint da API
'''

# Participantes
from core.models import Professor, Turma, Aluno, Participante
from core.utils import from_img_dir_to_bytes
from conftest import clear_data

class Teste_Participantes:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1.1 - Tentativa com turma não registrada
        response = client.get('/turmas/FAKECLASS/participantes/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 1.b - Tentativa com turma não registrada
        response = client.get('/turmas/FAKECLASS/participantes/1/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - Turma sem participantes
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.get('/turmas/SCC5900/participantes/', headers=headers)

        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 3 - OK
        mock_data = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_data))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        _db.session.commit()

        response = client.get('/turmas/SCC5900/participantes/', headers=headers)
        assert response.json[0]['matricula'] == '101010'

        response = client.get('/turmas/SCC5900/participantes/1/', headers=headers)
        assert response.json[0]['matricula'] == '101010'

        response = client.get('/turmas/SCC5900/participantes/?matricula=101010', headers=headers)
        assert response.json[0]['matricula'] == '101010'

        # CENÁRIO 4 - Tentativa de obter participante com ID sem registro no banco de dados
        response = client.get('/turmas/SCC5900/participantes/100/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe participante com esse ID no banco de dados dessa turma.'

        # CLEAN UP
        clear_data(_db)

    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)
        
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        # CENÁRIO 1 - Tentativa com turma não registrada
        response = client.post('/turmas/FAKECLASS/participantes/', data={'matricula': '1'}, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'
        
        
        # CENÁRIO 2 - Aluno com matrícula não registrada no banco de dados
        data = {
            "matricula": "101010",
        }
        response = client.post('/turmas/SCC5900/participantes/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matrícula no banco de dados.'

        # CENÁRIO 3 - OK
        mock_data = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_data))
        _db.session.commit()        

        response = client.post('/turmas/SCC5900/participantes/', data=data, headers=headers)

        assert response.status_code == 201
        assert response.json == {'participante.id': 1}

        # CENÁRIO 4 - Aluno já registrado na disciplina
        response = client.post('/turmas/SCC5900/participantes/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Esse aluno já foi registrado nessa disciplina.'

        # CLEAN UP
        clear_data(_db)


    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)

        mock_data = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')

        # CENÁRIO 1 - Tentativa com turma não registrada
        response = client.delete('/turmas/FAKECLASS/participantes/1/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - OK
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_data))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        _db.session.commit()
        response = client.delete('/turmas/SCC5900/participantes/1/', headers=headers)
        assert response.status_code == 204

        # CENÁRIO 3 - Tentativa de excluir aluno não mais participante
        response = client.delete('/turmas/SCC5900/participantes/1/', headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe participante com esse ID no banco de dados dessa turma.'

        # CLEAN UP
        clear_data(_db)


    