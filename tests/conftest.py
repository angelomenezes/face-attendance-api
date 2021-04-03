import pytest
import os, sys
sys.path.append('./')
from core.run import create_app
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session', autouse=True)
def get_client_db():
    app, _db = create_app(testing=True)

    with app.test_client() as client:
        with app.app_context():
            _db.app = app
            _db.create_all()
            headers = {
                'Authorization': 'Bearer {}'.format(create_access_token('test_user'))
            }
        yield client, _db, headers
    
    _db.session.close()
    os.remove('./core/test.db')

def clear_data(_db):
    meta = _db.metadata
    for table in reversed(meta.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()

#@pytest.fixture(scope='session', autouse=True)
def headers():
    access_token = create_access_token('test_user')
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    return headers
