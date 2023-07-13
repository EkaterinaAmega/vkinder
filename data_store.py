# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config import db_url_object

metadata = MetaData()
Base = declarative_base()


class Viewed(Base):
    __tablename__ = "viewed"
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


engine = create_engine(db_url_object)
Base.metadata.create_all(engine)

# Добавление записей из БД


def database_add_user(profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()


# Извлечение записей из БД


def database_check_user(profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = (
            session.query(Viewed)
            .filter(
                Viewed.profile_id == profile_id, Viewed.worksheet_id == worksheet_id
            )
            .first()
        )
        return True if from_bd else False
