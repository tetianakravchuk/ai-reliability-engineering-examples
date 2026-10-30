"""Standalone educational PostgreSQL transaction example; not WPH source code."""
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, text
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Checkpoint(Base):
    __tablename__ = 'checkpoints'
    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False, default=0)

class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, primary_key=True)
    checkpoint_id = Column(Integer, ForeignKey('checkpoints.id'), nullable=False)
    external_id = Column(String, nullable=False, unique=True)

class StaleCheckpoint(Exception):
    pass

def ingest(engine, checkpoint_id: int, expected_version: int, external_id: str):
    """Insert and CAS update in one transaction. Any failure rolls both back."""
    with Session(engine) as session:
        with session.begin():
            session.add(Observation(checkpoint_id=checkpoint_id, external_id=external_id))
            session.flush()
            result = session.execute(text('''
                UPDATE checkpoints SET version = version + 1
                WHERE id = :id AND version = :expected
            '''), {'id': checkpoint_id, 'expected': expected_version})
            if result.rowcount != 1:
                raise StaleCheckpoint('checkpoint changed; transaction rolled back')
