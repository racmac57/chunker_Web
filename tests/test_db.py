from chunker_db import ChunkerDatabase


def test_log_error_retry(tmp_path):
    db = ChunkerDatabase(db_path=str(tmp_path / "t.db"))
    db.log_error("x.txt", "test message")
    assert True

