'''
    Testes para cada endpoint da API
'''

# Frequencias
from core.models import Professor, Turma, Aluno, Participante, Frequencia
from core.utils import from_img_dir_to_bytes
from conftest import clear_data
import os
from numpy import array
from core.utils import process_faces, from_array_to_bytes

class Teste_Frequencias:
    def test_get(self, get_client_db):
        # GET
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Tentativa com turma não registrada
        response = client.get('/turmas/SCC5900/frequencias/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - Sem frequências registradas
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.get('/turmas/SCC5900/frequencias/', headers=headers)

        assert response.status_code == 200
        assert response.json == []

        # CENÁRIO 3 - OK
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        mock_data_img_turma = from_img_dir_to_bytes('./tests/test_images/ivete-e-boy.jpg')
        _db.session.add(Frequencia(turma_codigo='SCC5900', imagem_turma=mock_data_img_turma))
        _db.session.commit()

        response = client.get('/turmas/SCC5900/frequencias/', headers=headers)
        assert response.json[0]['id'] == 1

        # CLEAN UP
        clear_data(_db)
    
    def test_post(self, get_client_db):
        # POST
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Tentativa com turma não registrada
        file = os.path.join("./tests/test_images/ivete-e-boy.jpg")
        mock_data_img_turma = (file, './tests/test_images/ivete-e-boy.jpg')
        data = {
            "imagem_turma": mock_data_img_turma
        }

        response = client.post('/turmas/SCC5900/frequencias/', data=data, headers=headers)
        assert response.status_code == 400 
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - Tentativa com turma sem participantes
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.post('/turmas/SCC5900/frequencias/', data=data, headers=headers)
        assert response.status_code == 400 
        assert response.json['message'] == 'Não existem participantes registrados na turma.'
        
        # CENÁRIO 3 - OK
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        _db.session.commit()        
        
        response = client.post('/turmas/SCC5900/frequencias/', data=data, headers=headers)
        assert response.status_code == 201
        assert response.json == {'frequencia.id': 1}

        # CLEAN UP
        clear_data(_db)

    
    def test_put(self, get_client_db):
        # PUT
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Tentativa com turma não registrada
        file = os.path.join("./tests/test_images/ivete-e-boy.jpg")
        mock_data_img_turma = (file, './tests/test_images/ivete-e-boy.jpg')
        data = {
            "imagem_turma": mock_data_img_turma
        }

        response = client.put('/turmas/SCC5900/frequencias/1/', data=data, headers=headers)
        assert response.status_code == 400 # Já que não tem turma registrada
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - Tentativa com frequência não registrada
        _db.session.add(Professor(nome='AAA', departamento='AAA', instituicao='AAA'))
        _db.session.add(Turma(nome='Metodologia Cientifica', codigo='SCC5900', semestre="2020.2", professor_id=1))
        _db.session.commit()

        response = client.put('/turmas/SCC5900/frequencias/1/', data=data, headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'

        # CENÁRIO 3 - OK
        mock_img = from_img_dir_to_bytes('./tests/test_images/ivete.jpg')
        mock_face = array(process_faces(mock_img))
        mock_face_embedding = from_array_to_bytes(mock_face)
        _db.session.add(Aluno(nome='Ivete', curso='Danca', matricula='101010', embedding=mock_face_embedding))
        _db.session.add(Participante(turma_codigo='SCC5900', matricula='101010'))
        mock_data_img_turma = from_img_dir_to_bytes('./tests/test_images/ivete-e-boy.jpg')
        _db.session.add(Frequencia(turma_codigo='SCC5900', imagem_turma=mock_data_img_turma))
        _db.session.commit()

        response = client.put('/turmas/SCC5900/frequencias/1/', data=data, headers=headers)
        assert response.status_code == 204

        # CLEAN UP
        clear_data(_db)


    def test_delete(self, get_client_db):
        # DELETE
        client, _db, headers = get_client_db
        clear_data(_db)
        
        # CENÁRIO 1 - Tentativa com turma não registrada
        response = client.delete('/turmas/SCC5900/frequencias/1/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - OK
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

        response = client.delete('/turmas/SCC5900/frequencias/1/', headers=headers)
        assert response.status_code == 204

        # CENÁRIO 3 - Tentativa com frequência não mais presente
        response = client.delete('/turmas/SCC5900/frequencias/1/', headers=headers)
        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'

        # CLEAN UP
        clear_data(_db)


    