import pytest
from fastapi import HTTPException

from app.schemas.privacyClause_schema import PrivacyClauseCreate, PrivacyClauseUpdate
from app.services.privacyClause_service import (
    create_privacy_clause,
    delete_privacy_clause,
    load_privacy_clause,
    load_privacy_clauses,
    update_privacy_clause,
)


def _create(number=1, title="Datenschutz", description="Text", is_preamble=False) -> PrivacyClauseCreate:
    return PrivacyClauseCreate(number=number, title=title, description=description, is_preamble=is_preamble)


# ---------------------------------------------------------------------------
# load_privacy_clauses
# ---------------------------------------------------------------------------


def test_load_privacy_clauses_empty(db):
    assert load_privacy_clauses(db) == []


def test_load_privacy_clauses_ordered_by_number(db):
    create_privacy_clause(_create(number=3), db)
    create_privacy_clause(_create(number=1), db)
    create_privacy_clause(_create(number=2), db)

    result = load_privacy_clauses(db)
    assert [c.number for c in result] == [1, 2, 3]


# ---------------------------------------------------------------------------
# load_privacy_clause
# ---------------------------------------------------------------------------


def test_load_privacy_clause_found(db):
    clause = create_privacy_clause(_create(title="Meine Klausel"), db)
    result = load_privacy_clause(clause.clause_id, db)
    assert result.title == "Meine Klausel"


def test_load_privacy_clause_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        load_privacy_clause(99999, db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# create_privacy_clause
# ---------------------------------------------------------------------------


def test_create_privacy_clause_persists(db):
    clause = create_privacy_clause(_create(number=10, title="DSGVO", is_preamble=True), db)
    assert clause.clause_id is not None
    assert clause.title == "DSGVO"
    assert clause.is_preamble is True


def test_create_privacy_clause_is_preamble_defaults_false(db):
    clause = create_privacy_clause(_create(), db)
    assert clause.is_preamble is False


# ---------------------------------------------------------------------------
# update_privacy_clause
# ---------------------------------------------------------------------------


def test_update_privacy_clause_title(db):
    clause = create_privacy_clause(_create(title="Alt"), db)
    result = update_privacy_clause(clause.clause_id, PrivacyClauseUpdate(title="Neu"), db)
    assert result.title == "Neu"


def test_update_privacy_clause_is_preamble(db):
    clause = create_privacy_clause(_create(is_preamble=False), db)
    result = update_privacy_clause(clause.clause_id, PrivacyClauseUpdate(is_preamble=True), db)
    assert result.is_preamble is True


def test_update_privacy_clause_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        update_privacy_clause(99999, PrivacyClauseUpdate(title="x"), db)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# delete_privacy_clause
# ---------------------------------------------------------------------------


def test_delete_privacy_clause_removes_it(db):
    clause = create_privacy_clause(_create(), db)
    cid = clause.clause_id
    delete_privacy_clause(cid, db)

    with pytest.raises(HTTPException) as exc:
        load_privacy_clause(cid, db)
    assert exc.value.status_code == 404


def test_delete_privacy_clause_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        delete_privacy_clause(99999, db)
    assert exc.value.status_code == 404
