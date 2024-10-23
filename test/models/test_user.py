import pytest
import sqlalchemy
import sqlmodel

import models


def test_user_unique(db_session: sqlmodel.Session):
    user_1 = models.User(
        email="user-1@gmail.com",
        state=models.user.STATE_ENABLED,
        user_id="user-1",
    )

    db_session.add(user_1)
    db_session.commit()

    assert user_1.email == "user-1@gmail.com"
    assert user_1.user_id == "user-1"

    # email and user_id must be unique

    user_2 = models.User(
        email=user_1.email,
        state=models.user.STATE_ENABLED,
        user_id="user-2",
    )

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.add(user_2)
        db_session.commit()

    db_session.rollback()

    user_2 = models.User(
        email="user-2@gmail.com",
        state=models.user.STATE_ENABLED,
        user_id=user_1.user_id,
    )

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.add(user_2)
        db_session.commit()
