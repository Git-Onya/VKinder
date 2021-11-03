from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, PrimaryKeyConstraint
from application.config import DSN

engine = create_engine(DSN, echo=True)
Base = declarative_base()


class Pair(Base):
    __tablename__ = 'pair'

    pair_id = Column(Integer, primary_key=True)
    pair_name = Column(String(100), nullable=False)
    link = Column(String(250), nullable=False)
    top_photo = Column(String(50), nullable=False)


class Bonds(Base):
    __tablename__ = 'bonds'
    __table_args__ = (PrimaryKeyConstraint('seeker_id', 'pair_id', name='bond'),)
    seeker_id = Column(Integer, primary_key=True)
    pair_id = Column(Integer, primary_key=True)
    favorite = Column(Boolean)
    blacklist = Column(Boolean)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
