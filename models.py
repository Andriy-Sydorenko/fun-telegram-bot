from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    pseudonym = Column(String)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    full_name = Column(String)
    telegram_id = Column(Integer)
    joined_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __str__(self) -> str:
        return self.username if self.username else self.full_name
