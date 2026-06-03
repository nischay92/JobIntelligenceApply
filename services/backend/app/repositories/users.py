from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_google_sub(self, google_sub: str) -> User | None:
        return self.db.scalar(select(User).where(User.google_sub == google_sub))

    def upsert_google_user(
        self,
        *,
        google_sub: str,
        email: str,
        name: str,
        avatar_url: str | None,
    ) -> User:
        user = self.get_by_google_sub(google_sub)
        if user is None:
            user = User(
                google_sub=google_sub,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
            self.db.add(user)
        else:
            user.email = email
            user.name = name
            user.avatar_url = avatar_url

        self.db.commit()
        self.db.refresh(user)
        return user
