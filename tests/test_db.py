from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(username='test', email='test@test.com', password='secret')
    session.add(user)
    session.commit()
    # session.refresh(user)
    result = session.scalar(select(User).where(User.email == 'test@test.com'))

    # assert user.id == 1
    assert result.username == 'test'
    assert result.id == 1
