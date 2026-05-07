import pytest
from fastapi import HTTPException

from app.schemas.therapyClause_schema import TherapyClauseCreate, TherapyClauseUpdate
from app.services.therapyClause_service import (
    create_clause,
    delete_clause,
    load_clause,
    load_clauses,
    update_clause,
)


def _create(number=1, title="Titel", description="Beschreibung") -> TherapyClauseCreate:
    return TherapyClauseCreate(number=number, title=title, description=description)


# ---------------------------------------------------------------------------
# load_clauses
# ---------------------------------------------------------------------------


def test_load_clauses_empty(db):
    assert load_clauses(db) == []


def test_load_clauses_ordered_by_number(db):
    create_clause(_create(number=3, title="C"), db)
    create_clause(_create(number=1, title="A"), db)
    create_clause(_create(number=2, title="B"), db)

    result = load_clauses(db)
    assert [c.number for c in result] == [1, 2, 3]


# ---------------------------------------------------------------------------
# load_clause
# ---------------------------------------------------------------------------


def test_load_clause_found(db):
    clause = create_clause(_create(), db)
    result = load_clause(clause.clause_id, db)
    assert result.clause_id == clause.clause_id
    assert result.title == "Titel"


def test_load_clause_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        load_clause(99999, db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# create_clause
# ---------------------------------------------------------------------------


def test_create_clause_persists(db):
    clause = create_clause(_create(number=5, title="Neue Klausel", description="Text"), db)
    assert clause.clause_id is not None
    assert clause.title == "Neue Klausel"
    assert clause.number == 5

    loaded = load_clause(clause.clause_id, db)
    assert loaded.description == "Text"


# ---------------------------------------------------------------------------
# update_clause
# ---------------------------------------------------------------------------


def test_update_clause_title(db):
    clause = create_clause(_create(title="Alt"), db)
    result = update_clause(clause.clause_id, TherapyClauseUpdate(title="Neu"), db)
    assert result.title == "Neu"
    assert result.number == clause.number  # unchanged


def test_update_clause_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        update_clause(99999, TherapyClauseUpdate(title="x"), db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# delete_clause
# ---------------------------------------------------------------------------


def test_delete_clause_removes_it(db):
    clause = create_clause(_create(), db)
    cid = clause.clause_id
    delete_clause(cid, db)

    with pytest.raises(HTTPException) as exc:
        load_clause(cid, db)
    assert exc.value.status_code == 404


def test_delete_clause_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        delete_clause(99999, db)
    assert exc.value.status_code == 404
