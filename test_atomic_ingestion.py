import os
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from atomic_ingestion import Base, Checkpoint, Observation, StaleCheckpoint, ingest

@pytest.fixture
def engine():
    url = os.getenv('TEST_DATABASE_URL')
    if not url or not url.startswith('postgresql'):
        pytest.skip('Set TEST_DATABASE_URL to a disposable PostgreSQL database')
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as s, s.begin():
        s.add(Checkpoint(id=1, version=0))
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

def counts(engine):
    with Session(engine) as s:
        return (s.scalar(select(func.count()).select_from(Observation)), s.get(Checkpoint, 1).version)

def test_stale_update_rolls_back_observation(engine):
    ingest(engine, 1, 0, 'book-a')
    with pytest.raises(StaleCheckpoint):
        ingest(engine, 1, 0, 'book-b')
    assert counts(engine) == (1, 1)

def test_two_workers_one_commit(engine):
    def worker(external_id):
        try:
            ingest(engine, 1, 0, external_id)
            return 'committed'
        except StaleCheckpoint:
            return 'stale'
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(worker, ['book-a', 'book-b']))
    assert sorted(results) == ['committed', 'stale']
    assert counts(engine) == (1, 1)

def test_interrupted_transaction_rolls_back_observation(engine):
    """A failure after inserting data must leave the database unchanged."""
    from sqlalchemy import text
    with pytest.raises(RuntimeError, match="simulated crash"):
        with Session(engine) as session:
            with session.begin():
                session.add(Observation(checkpoint_id=1, external_id="book-interrupted"))
                session.flush()
                session.execute(text(
                    "UPDATE checkpoints SET version = version + 1 WHERE id = :id"
                ), {"id": 1})
                raise RuntimeError("simulated crash")
    assert counts(engine) == (0, 0)

def test_duplicate_external_id_is_rejected(engine):
    """The unique identifier prevents replay duplicates."""
    from sqlalchemy.exc import IntegrityError
    ingest(engine, 1, 0, "book-a")
    with pytest.raises(IntegrityError):
        ingest(engine, 1, 1, "book-a")
    assert counts(engine) == (1, 1)
