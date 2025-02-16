from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Ola mundo'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    # user_with_id = UserDB(id=len(database) + 1, **user.model_dump())
    # database.append(user_with_id)
    # return user_with_id

    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if not db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Username already exists',
        )
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(
    session=Depends(get_session),
    limit: int = 10,
    offset: int = 0,
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_users_id(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_users(
    user_id: int,
    user: UserSchema,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    # db_user = session.scalar(select(User).where(User.id == user_id))
    # if not db_user:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    #     )
    # db_user.email = user.email
    # db_user.username = user.username
    # db_user.password = get_password_hash(user.password)
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail='Not enough permission')
    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_users(
    user_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    # db_user = session.scalar(select(User).where(User.id == user_id))
    # if not db_user:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    #     )
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail='Not enough permission')
    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted!'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Incorrect email or password'
        )
    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
