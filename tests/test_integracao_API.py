import os
from conftest import clear_data

file_ivete = os.path.join("./tests/test_images/ivete.jpg")
img_file_ivete = (file_ivete, './tests/test_images/ivete.jpg')

aluno_1 = {
    "nome": "Ivete",
    "curso": "Musica",
    "matricula": "101010",
    "imagem_aluno": img_file_ivete
}

file_vinny = os.path.join("./tests/test_images/vinicius.png")
img_file_vinny = (file_vinny, './tests/test_images/vinicius.png')

aluno_2 = {
    "nome": "Vinicius",
    "curso": "Dança",
    "matricula": "202020",
    "imagem_aluno": img_file_vinny
}

professor = {
    "nome": "Angelo",
    "departamento": "Ciencia da Computacao",
    "instituicao": "UFS"
}

turma = {
    "nome": "Metodologia Científica",
    "codigo": "SCC5900",
    "semestre": "2021.2",
    "professor_id": 1
}

file_turma_cenario_1 = os.path.join("./tests/test_images/ivete-e-boy.jpg")
img_turma_cenario_1 = (file_turma_cenario_1, './tests/test_images/ivete-e-boy.jpg')

frequencia_cenario_1 = {
    "imagem_turma": img_turma_cenario_1
}

file_turma_cenario_2 = os.path.join("./tests/test_images/fitdance-3faces.jpg")
img_turma_cenario_2 = (file_turma_cenario_2, './tests/test_images/fitdance-3faces.jpg')

frequencia_cenario_2 = {
    "imagem_turma": img_turma_cenario_2
}

file_turma_cenario_3 = os.path.join("./tests/test_images/random_class.jpg")
img_turma_cenario_3 = (file_turma_cenario_3, './tests/test_images/random_class.jpg')

frequencia_cenario_3 = {
    "imagem_turma": img_turma_cenario_3
}

### Testes de Integração da API em alguns cenários prováveis de aplicação
class Testes_de_Integracao:    
    def test_registro_basico_participantes(self, get_client_db):
        client, _db, headers = get_client_db
        clear_data(_db)

        # CENÁRIO 1 - Registro da estrutura básica para registro de presença (Aluno, Professor, Turma e registro como Participante)
        client.post('/alunos/', data=aluno_1, headers=headers)
        client.post('/alunos/', data=aluno_2, headers=headers)
        client.post('/professores/', data=professor, headers=headers)
        client.post('/turmas/', data=turma, headers=headers)
        client.post('/turmas/SCC5900/participantes/', data={'matricula': aluno_1['matricula']}, headers=headers)
        client.post('/turmas/SCC5900/participantes/', data={'matricula': aluno_2['matricula']}, headers=headers)

        response = client.get('/turmas/SCC5900/participantes/', headers=headers)

        assert response.json[0]['matricula'] == aluno_1['matricula']
        assert response.json[1]['matricula'] == aluno_2['matricula']

        clear_data(_db)

    def test_registro_frequencia_presenca(self, get_client_db):
        client, _db, headers = get_client_db
        clear_data(_db)

        client.post('/alunos/', data=aluno_1, headers=headers)
        client.post('/alunos/', data=aluno_2, headers=headers)
        client.post('/professores/', data=professor, headers=headers)
        client.post('/turmas/', data=turma, headers=headers)
        client.post('/turmas/SCC5900/participantes/', data={'matricula': aluno_1['matricula']}, headers=headers)
        client.post('/turmas/SCC5900/participantes/', data={'matricula': aluno_2['matricula']}, headers=headers)
        
        # CENÁRIO 1 - Aluno 1 está presente e o Aluno 2 não
        response = client.post('/turmas/SCC5900/frequencias/', data=frequencia_cenario_1, headers=headers)
        frequencia_id = response.json['frequencia.id'] 
        response = client.get(f'/turmas/SCC5900/frequencias/{frequencia_id}/presencas/', headers=headers)

        assert response.json[0]['status'] == True
        assert response.json[1]['status'] == False

        # CENÁRIO 2 - Aluno 1 e Aluno 2 estão presentes
        response = client.post('/turmas/SCC5900/frequencias/', data=frequencia_cenario_2, headers=headers)
        frequencia_id = response.json['frequencia.id'] 
        response = client.get(f'/turmas/SCC5900/frequencias/{frequencia_id}/presencas/', headers=headers)

        assert response.json[0]['status'] == True
        assert response.json[1]['status'] == True

        # CENÁRIO 3 - Aluno 1 e Aluno 2 não estão presentes
        response = client.post('/turmas/SCC5900/frequencias/', data=frequencia_cenario_3, headers=headers)
        frequencia_id = response.json['frequencia.id'] 
        response = client.get(f'/turmas/SCC5900/frequencias/{frequencia_id}/presencas/', headers=headers)

        assert response.json[0]['status'] == False
        assert response.json[1]['status'] == False

        clear_data(_db)

    def test_anotacao_erros(self, get_client_db):
        client, _db, headers = get_client_db
        clear_data(_db)

        client.post('/alunos/', data=aluno_1, headers=headers)
        client.post('/alunos/', data=aluno_2, headers=headers)
        client.post('/professores/', data=professor, headers=headers)
        client.post('/turmas/', data=turma, headers=headers)
        client.post('/turmas/SCC5900/participantes/', data={'matricula': aluno_1['matricula']}, headers=headers)
        client.post('/turmas/SCC5900/participantes/', data={'matricula': aluno_2['matricula']}, headers=headers)
        client.post('/turmas/SCC5900/frequencias/', data=frequencia_cenario_1, headers=headers)

        # CENÁRIO 1 - Corrigir a presença no cenário 1 para dizer que o Aluno 2 na verdade está presente e checar anotação do erro (falso negativo)
        client.put(f'/turmas/SCC5900/frequencias/1/presencas/', data={'matricula': 202020, 'status': True}, headers=headers)
        response = client.get(f'/turmas/SCC5900/frequencias/1/erros/', headers=headers)

        assert response.json[0]['falsos_positivos'] == 0
        assert response.json[0]['falsos_negativos'] == 1

        # CENÁRIO 2 - Corrigir a presença no cenário 1 para dizer que o Aluno 1 na verdade faltou e checar anotação do erro (falso positivo)
        client.put(f'/turmas/SCC5900/frequencias/1/presencas/', data={'matricula': 101010, 'status': False}, headers=headers)
        response = client.get(f'/turmas/SCC5900/frequencias/1/erros/', headers=headers)

        assert response.json[0]['falsos_positivos'] == 1
        assert response.json[0]['falsos_negativos'] == 1

        clear_data(_db)
        