# Storage layer

Database models, engine management, image/thumbnail storage and staging.

- **Imports nothing from `matcher`/`detection`/`services`/`api`.** The storage layer is a
  leaf dependency — other layers import it, it imports none of them.
- **Tests:** `backend/tests/storage/`

## Engine fixture teardown

Always `yield` the engine and call `engine.dispose()` afterwards — not `return`. Without
dispose, Python 3.13 raises `ResourceWarning: unclosed database` for every connection in
the pool, which fails the zero-warnings gate.

```python
@pytest.fixture()
def engine(tmp_path):
    e = make_engine(tmp_path / "test.db")
    init_db(e)
    yield e
    e.dispose()
```

## Parent/child insert ordering

SQLModel has no ORM relationship between `GarmentRow` and `GarmentColourRow`, so
SQLAlchemy does not know insertion order. Call `session.flush()` after adding the parent
row before adding child rows, or the FK constraint fires on the child insert.
