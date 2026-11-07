"""Tiny in-memory case store so /chat knows which scan result is being discussed.
Swap for a database (SQLite/Postgres) when you need persistence."""
from collections import OrderedDict
from threading import Lock

from app.schemas import AnalysisResponse

_MAX = 200
_cases: "OrderedDict[str, AnalysisResponse]" = OrderedDict()
_lock = Lock()


def save_case(case: AnalysisResponse) -> None:
    with _lock:
        _cases[case.caseId] = case
        while len(_cases) > _MAX:
            _cases.popitem(last=False)


def get_case(case_id: str | None) -> AnalysisResponse | None:
    if not case_id:
        return None
    with _lock:
        return _cases.get(case_id)
