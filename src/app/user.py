from flask_login import UserMixin

from src.app.database.db import get_db


class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2]
        )
        return user

    def create(self):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email)"
            " VALUES (?, ?, ?)",
            (self.id, self.name, self.email),
        )
        db.commit()