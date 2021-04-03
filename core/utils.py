from core.models import Aluno, AlunoSchema, Participante
import numpy as np
from numpy.linalg import norm
from flask import abort
import io
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import torchvision.transforms as transforms
from copy import deepcopy
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps

def token_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            return fn(*args, **kwargs)
        return decorator
    return wrapper


if torch.cuda.is_available():
    current_device = torch.device('cuda')
else:
    current_device = torch.device('cpu')


face_detector = MTCNN(keep_all=True, device=current_device)
feature_extractor = InceptionResnetV1(pretrained='vggface2').eval()


def timestamp_to_datetime_object(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')


def find_faces(img_bytes):
    
    face_list = []
    
    img = Image.open(io.BytesIO(img_bytes))

    # Detect faces
    boxes, _ = face_detector.detect(img)
    
    # Check if any face was found
    found_faces = not (str(type(boxes)) == "<class 'NoneType'>")

    if found_faces:
        for box in boxes:
            cropped_face = img.crop(box.tolist()).resize((160,160), resample=Image.BICUBIC)
            face_list.append(cropped_face)

    return face_list


def from_img_dir_to_bytes(directory):
    img = Image.open(directory)
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='JPEG')
    return imgByteArr.getvalue()


def from_array_to_bytes(array):
    imgByteArr = io.BytesIO()
    np.save(imgByteArr, array)
    imgByteArr.seek(0)
    return imgByteArr.read()


def resize_img_bytes(img_bytes):
    imgByteArr = io.BytesIO()
    img = Image.open(io.BytesIO(img_bytes)).resize((512, 256), resample=Image.BICUBIC)
    img.save(imgByteArr, format='JPEG')
    return imgByteArr.getvalue()


def obter_threshold(lista_de_faces_da_turma):
    
    similaridade_maxima = 0
    
    for face1 in lista_de_faces_da_turma:
        for face2 in lista_de_faces_da_turma:
            similaridade = cos_sim(face1[0], face2[0])
            if similaridade > similaridade_maxima and similaridade != 1.0:
                similaridade_maxima = similaridade
    
    return similaridade_maxima


def obter_presenca(matriculas, embedding_participantes, embeddings_do_dia, threshold=0.49):
    
    embeddings_restantes = deepcopy(embedding_participantes)
    matriculas_restantes = deepcopy(matriculas)
    status_presenca = {aluno: False for aluno in matriculas}

    for index, pessoa_na_aula in enumerate(embeddings_do_dia):
        
        similaridades = []
        
        for feature_aluno, matricula_aluno in zip(embeddings_restantes, matriculas_restantes):
            similaridades.append(cos_sim(feature_aluno, pessoa_na_aula))
            #print(f'Similaridade da pessoa {index+1} com {matricula_aluno} foi de: {cos_sim(feature_aluno, pessoa_na_aula)}')
        
        #print('\n')

        maxima_similaridade = max(similaridades)
        index_aluno_mais_parecido = similaridades.index(maxima_similaridade)
    
        if maxima_similaridade > threshold and maxima_similaridade != 1.0:
            # Muda o status do aluno para presente
            status_presenca[matriculas_restantes[index_aluno_mais_parecido]] = True
            #print(f'Aluno {matriculas_restantes[index_aluno_mais_parecido]} esta presente')
            
            # Remove esse aluno da lista de participantes aptos a serem reconhecidos
            del matriculas_restantes[index_aluno_mais_parecido]
            del embeddings_restantes[index_aluno_mais_parecido]
        
        if len(matriculas_restantes) == 0: # Se todas as matriculas já estiverem sido analisadas, break
            break

    return status_presenca


def get_face_features(face_list):
    
    face_embeddings = []

    for face in face_list:
        face_as_tensor = transforms.ToTensor()(face).unsqueeze(0)
        face_embeddings.append(feature_extractor(face_as_tensor).squeeze(0).detach().numpy())

    return face_embeddings


def process_faces(img_bytes):
    faces_found = find_faces(img_bytes)
    features = get_face_features(faces_found)
    return features


def cos_sim(a,b): 
    return np.dot(a, b)/(norm(a)*norm(b))


def obter_aluno_pela_matricula(lista_matricula):
    lista_de_alunos = [Aluno.query.filter_by(matricula=matricula).all()[0] for matricula in lista_matricula]
    return AlunoSchema(many=True, only=('nome', 'matricula', 'curso')).dump(lista_de_alunos)


def checar_presenca_da_turma(turma_codigo, img_turma):
    
    face_embeddings_do_dia = np.array(process_faces(img_turma))

    if len(face_embeddings_do_dia) < 1:
            abort(400, 'Não foram detectadas faces na imagem enviada.')

    # Obtenção da matricula dos participantes
    alunos_participantes = Participante.query.filter_by(turma_codigo=turma_codigo)
    matricula_participantes = [aluno.matricula for aluno in alunos_participantes.all()]

    # Obtencao dos embeddings dos participantes
    embedding_participantes = [Aluno.query.filter_by(matricula=matricula).all()[0].embedding for matricula in matricula_participantes]
    embedding_participantes = [np.load(io.BytesIO(data)) for data in embedding_participantes]
    
    # Similaridade tem que ser acima de 49%
    return obter_presenca(matricula_participantes, embedding_participantes, face_embeddings_do_dia, threshold=0.49)

def clear_parser(dictionary):
    '''
    Limpa o dicionário de chaves com valores 'None'
    '''
    return {k: v for k, v in dictionary.items() if v is not None}

