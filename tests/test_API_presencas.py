'''
    Testes para cada endpoint da API
'''

# Presencas
from core.models import AnotacaoErros, Presenca, Professor, Turma, Aluno, Participante, Frequencia
from core.utils import from_img_dir_to_bytes
from conftest import clear_data
from numpy import array
from core.utils import process_faces, from_array_to_bytes

class Teste_Presencas:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        mock_data_img_turma = from_img_dir_to_bytes('./tests/test_images/ivete-e-boy.jpg')
        _db.session.add(Frequencia(turma_codigo='SCC5900', imagem_turma=mock_data_img_turma))
        _db.session.add(Presenca(frequencia_id=1, participante_id=1, status=True))
        _db.session.commit()

        # CENÁRIO 1 - OK
        response = client.get('/turmas/SCC5900/frequencias/1/presencas/', headers=headers)
        assert response.status_code == 200
        assert response.json[0]['participante_id'] == 1
        assert response.json[0]['matricula'] == '101010'
        assert response.json[0]['status'] == True

        response = client.get('/turmas/SCC5900/frequencias/1/presencas/?matricula=101010', headers=headers)
        assert response.status_code == 200
        assert response.json[0]['status'] == True

        response = client.get('/turmas/SCC5900/frequencias/1/presencas/?participante_id=1', headers=headers)
        assert response.status_code == 200
        assert response.json[0]['status'] == True

        # CENÁRIO 2 - Tentativa de acesso com código de turma não existente no banco de dados
        response = client.get('/turmas/FAKECLASS/frequencias/1/presencas/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 3 - Tentativa de acesso com ID de frequência não existente no banco de dados
        response = client.get('/turmas/SCC5900/frequencias/100/presencas/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'

        # CLEAN UP
        clear_data(_db)
    
    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)

        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        mock_data_img_turma = from_img_dir_to_bytes('./tests/test_images/ivete-e-boy.jpg')
        _db.session.add(Frequencia(turma_codigo='SCC5900', imagem_turma=mock_data_img_turma))
        _db.session.commit()

        # CENÁRIO 1 - Matrícula inválida
        data = {
            "matricula": 101011,
            "status": True
        }

        response = client.post('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matricula participando da disciplina no banco de dados.'

        # CENÁRIO 2 - OK
        data = {
            "matricula": 101010,
            "status": True
        }

        response = client.post('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)

        assert response.status_code == 201
        assert response.json == {'participante.id': 1}

        # CENÁRIO 3 - Aluno não registrado
        response = client.post('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Registro de presença desse aluno já está presente no banco de dados.'

        # CENÁRIO 4 - Não existe turma com o código indicado
        response = client.post('/turmas/FAKECLASS/frequencias/1/presencas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'
        
        # CENÁRIO 5 - Não existe frequencia com o ID indicado
        response = client.post('/turmas/SCC5900/frequencias/100/presencas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'
        
        # CLEAN UP
        clear_data(_db)

    
    def test_put(self, get_client_db):
        # PUT
        client, _db, headers = get_client_db
        clear_data(_db)

        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        mock_data_img_turma = from_img_dir_to_bytes('./tests/test_images/ivete-e-boy.jpg')
        _db.session.add(Frequencia(turma_codigo='SCC5900', imagem_turma=mock_data_img_turma))
        _db.session.add(Presenca(frequencia_id=1, participante_id=1, status=True))
        _db.session.add(AnotacaoErros(frequencia_id=1, falsos_positivos=0, falsos_negativos=0))
        _db.session.commit()

        # CENÁRIO 1 - Matrícula Inválida
        data = {
            "matricula": 202020,
            "status": True
        }

        response = client.put('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matricula participando da disciplina no banco de dados.'

        # CENÁRIO 2 - OK
        data = {
            "matricula": 101010,
            "status": False
        }

        response = client.put('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)
        assert response.status_code == 204

        # CENÁRIO 3 - Aluno sem presença registrada
        Presenca.query.filter_by(frequencia_id=1, participante_id=1).delete()
        _db.session.commit()

        response = client.put('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Aluno não possui presença registrada nesse dia no banco de dados.'

        # CENÁRIO 4 - Não existe turma com o código indicado
        response = client.put('/turmas/FAKECLASS/frequencias/1/presencas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'
        
        # CENÁRIO 5 - Não existe frequencia com o ID indicado
        response = client.put('/turmas/SCC5900/frequencias/100/presencas/', data=data, headers=headers)
        
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'

        # CLEAN UP
        clear_data(_db)

    
    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)
        
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        mock_data_img_turma = from_img_dir_to_bytes('./tests/test_images/ivete-e-boy.jpg')
        _db.session.add(Frequencia(turma_codigo='SCC5900', imagem_turma=mock_data_img_turma))
        _db.session.add(Presenca(frequencia_id=1, participante_id=1, status=True))
        _db.session.add(AnotacaoErros(frequencia_id=1, falsos_positivos=0, falsos_negativos=0))
        _db.session.commit()

        # CENÁRIO 1 - Matrícula inválida
        data = {
            "matricula": 202020,
         }
        response = client.delete('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe aluno com essa matricula participando da disciplina no banco de dados.'

        # CENÁRIO 2 - OK
        data = {
            "matricula": 101010,
        }
        response = client.delete('/turmas/SCC5900/frequencias/1/presencas/', data=data, headers=headers)
        assert response.status_code == 204

        # CENÁRIO 3 - Não existe turma com o código indicado
        response = client.delete('/turmas/FAKECLASS/frequencias/1/presencas/', data=data, headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'
        
        # CENÁRIO 4 - Não existe frequencia com o ID indicado
        response = client.delete('/turmas/SCC5900/frequencias/100/presencas/', data=data, headers=headers)
        
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'

        # CLEAN UP
        clear_data(_db)


    