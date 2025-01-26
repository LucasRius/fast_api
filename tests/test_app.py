# from http import HTTPStatus

# from fastapi.testclient import TestClient

# from fast_zero.app import app


# def test_read_root_deve_retornar_ok_e_ola_mundo():
#     client = TestClient(app)
#     response = client.get('/')

#     assert response.status_code == HTTPStatus.OK
#     assert response.json() == {'message': 'Ola mundo'}
from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import (
    app,  # Supondo que o código que você enviou esteja no arquivo 'main.py'
)

client = TestClient(app)


def test_read_root():
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Ola mundo'}
