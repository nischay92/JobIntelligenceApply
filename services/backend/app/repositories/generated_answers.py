from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import GeneratedAnswer


class GeneratedAnswerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: str,
        resume_id: str,
        job_id: str,
        content_type: str,
        prompt_label: str | None,
        content: str,
        metadata: dict | None,
        vector_id: str | None,
    ) -> GeneratedAnswer:
        generated = GeneratedAnswer(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            content_type=content_type,
            prompt_label=prompt_label,
            content=content,
            extra_metadata=metadata,
            vector_id=vector_id,
            status="draft",
        )
        self.db.add(generated)
        self.db.commit()
        self.db.refresh(generated)
        return generated

    def list_for_user(self, user_id: str, *, limit: int = 50) -> list[GeneratedAnswer]:
        return list(
            self.db.scalars(
                select(GeneratedAnswer)
                .options(joinedload(GeneratedAnswer.job), joinedload(GeneratedAnswer.resume))
                .where(GeneratedAnswer.user_id == user_id)
                .order_by(GeneratedAnswer.created_at.desc())
                .limit(limit)
            )
        )

    def get_for_user(self, *, user_id: str, answer_id: str) -> GeneratedAnswer | None:
        return self.db.scalar(
            select(GeneratedAnswer)
            .options(joinedload(GeneratedAnswer.job), joinedload(GeneratedAnswer.resume))
            .where(GeneratedAnswer.user_id == user_id, GeneratedAnswer.id == answer_id)
        )

    def update(self, answer: GeneratedAnswer, *, content: str | None, status: str | None) -> GeneratedAnswer:
        if content is not None:
            answer.content = content
        if status is not None:
            answer.status = status
        self.db.commit()
        self.db.refresh(answer)
        return answer
