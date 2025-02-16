from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Ola mundo'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testeuser',
            'password': 'testepass',
            'email': 'teste@email.com',
        },
    )
    assert response.status_code == (HTTPStatus.CREATED)
    assert response.json() == {
        'username': 'testeuser',
        'id': 1,
        'email': 'teste@email.com',
    }


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_users_id(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema
    # assert response.json() == {
    #     'id': 1,
    #     'username': 'testeuser',
    #     'email': 'teste@email.com',
    # }


def test_non_existing_read_users_id(client, user):
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_users(client, token, user):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'id': user.id,
            'username': 'testeuser',
            'password': 'testepass2',
            'email': 'teste@email.com',
        },
    )
    assert response.json() == {
        'username': 'testeuser',
        'id': user.id,
        'email': 'teste@email.com',
    }


def test_update_non_existing_user(client, token):
    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'id': 999,
            'username': 'testeuser2',
            'password': 'testepass',
            'email': 'teste2@email.com',
        },
    )

    CONST_400 = 400
    # assert response.status_code == HTTPStatus.NOT_FOUND
    # assert response.json() == {'detail': 'User not found'}
    assert response.status_code == CONST_400
    assert response.json() == {'detail': 'Not enough permission'}


def test_delete_users(client, token, user):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == {'message': 'User deleted!'}


def test_delete_non_existing_user(client, token):
    response = client.delete(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    CONST_400 = 400
    # assert response.status_code == HTTPStatus.NOT_FOUND
    # assert response.json() == {'detail': 'User not found'}
    assert response.status_code == CONST_400
    assert response.json() == {'detail': 'Not enough permission'}


def test_create_user_with_duplicate_email(client, user):
    # Testando a criação de um usuário com email duplicado
    user_data = {
        'username': 'newuser',
        'email': 'teste@email.com',
        'password': 'password123',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Email already exists'


def test_create_user_with_duplicate_username(client, user):
    # Testando a criação de um usuário com nome de usuário duplicado
    user_data = {
        'username': 'testeuser',
        'email': 'newuser@example.com',
        'password': 'password123',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Username already exists'


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_non_existing_user(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': 'wrong_pass'},
    )
    CONST_400 = 400
    assert response.status_code == CONST_400
    assert response.json()['detail'] == 'Incorrect email or password'


def test_credentials_exception_get_current_PyJWTError(client, user):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': 'Bearer 1234'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
