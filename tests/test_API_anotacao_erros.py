'''
    Testes para cada endpoint da API
'''

# Anotacao dos Erros
from core.models import AnotacaoErros, Presenca, Professor, Turma, Aluno, Participante, Frequencia
from core.utils import from_img_dir_to_bytes
from conftest import clear_data
from numpy import array
from core.utils import process_faces, from_array_to_bytes

class Teste_Anotacao_Erros:
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
        _db.session.add(AnotacaoErros(frequencia_id=1, falsos_positivos=1, falsos_negativos=0))
        _db.session.commit()


        # CENÁRIO 1 - Tentativa com turma não registrada
        response = client.get('/turmas/FAKECLASS/frequencias/1/erros/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe turma com esse codigo no banco de dados.'

        # CENÁRIO 2 - Tentativa com frequência não registrada
        response = client.get('/turmas/SCC5900/frequencias/100/erros/', headers=headers)

        assert response.status_code == 400
        assert response.json['message'] == 'Não existe frequencia com esse ID no banco de dados.'

        # CENÁRIO 3 - OK
        response = client.get('/turmas/SCC5900/frequencias/1/erros/', headers=headers)

        assert response.json[0]['frequencia_id'] == 1
        assert response.json[0]['falsos_positivos'] == 1
        assert response.json[0]['falsos_negativos'] == 0

        # CLEAN UP
        clear_data(_db)