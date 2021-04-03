import os
import sys
sys.path.append('./')
from APIs import api
from config import app, db
from flask import jsonify
from flask_jwt_extended import JWTManager

def create_app(testing=False):
    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    else:
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Para leitura de configuracoes chave secreta JWT
    if os.getenv('ENV_FILE_LOCATION'):
        app.config.from_envvar('ENV_FILE_LOCATION')
    elif os.getenv('JWT_SECRET_KEY'): # Travis CI
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    else:
        raise ValueError("Chave secreta não foi específicada para aplicação Flask.")

    db.init_app(app)
    api.init_app(app)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify(message="Token já expirou."), 401

    @jwt.invalid_token_loader
    def my_invalid_token_callback(error):
        return jsonify(message="Token inválida"), 401

    @jwt.unauthorized_loader
    def unauthorized_token_callback(error):
        return jsonify(message="O header de autorização não está presente."), 401

    return app, db

if __name__ == '__main__':
    app, _ = create_app(testing=False)
    app.run(debug=False)