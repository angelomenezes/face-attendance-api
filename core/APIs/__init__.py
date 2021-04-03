import sys
sys.path.append('../')
from .alunos import api as alunos_namespace
from .professores import api as professores_namespace
from .turmas import api as turmas_namespace
from .users import api as users_namespace
from .participantes import api as participantes_namespace
from .frequencias import api as frequencias_namespace
from .presencas import api as presencas_namespace
from .anotacao_erros import api as erros_namespace
from .frontend_variaveis import api as frontend_namespace
from flask_restx import Api

authorizations = {
    'JWT Bearer Token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

api = Api( 
    version='1.0', 
    title='Automatic Attendance API',
    description='API para automação do processo de chamadas de uma sala de aula via reconhecimento facial. <style>.models{display: none !important}</style>',
    authorizations=authorizations, 
    security='JWT Bearer Token',
)

api.add_namespace(users_namespace)
api.add_namespace(alunos_namespace)
api.add_namespace(professores_namespace)
api.add_namespace(turmas_namespace)
api.add_namespace(participantes_namespace, path='/turmas')
api.add_namespace(frequencias_namespace, path='/turmas')
api.add_namespace(presencas_namespace, path='/turmas')
api.add_namespace(erros_namespace, path='/turmas')
api.add_namespace(frontend_namespace)

