from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from src import orders


@pytest.fixture
def temp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "orders.db"
    real_connect = sqlite3.connect

    conn = real_connect(db_path)
    conn.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items TEXT,
            total REAL
        )
        """
    )
    conn.close()

    monkeypatch.setattr(
        orders.sqlite3,
        "connect",
        lambda _name: real_connect(db_path),
    )

    return db_path

@pytest.mark.parametrize(
    "order",
    [
        {"customer_name": "", "items": [{"price": 10, "qty": 2}], "total": 20},
        {"customer_name": "Alice", "items": [], "total": 0},
        {"customer_name": "Alice", "items": [{"price": -10, "qty": 2}], "total": -20},
        {"customer_name": "Alice", "items": [{"price": 10, "qty": 0}], "total": 0},
        {"customer_name": "Alice", "items": [{"price": 10, "qty": 1.5}], "total": 15},
        {"customer_name": "Alice", "items": [{"price": 10, "qty": 2}], "total": 21},
    ],
)
def test_save_order_rejects_invalid_input(
    temp_db: Path,
    order: dict[str, Any],
) -> None:
    assert orders.save_order(order) is False

    with sqlite3.connect(temp_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    assert count == 0


def test_save_order_accepts_valid_order(temp_db: Path) -> None:
    order = {
        "customer_name": "Alice",
        "items": [
            {"price": 10, "qty": 2},
            {"price": 5.5, "qty": 1},
        ],
        "total": 25.5,
    }

    assert orders.save_order(order) is True

    with sqlite3.connect(temp_db) as conn:
        row = conn.execute(
            "SELECT customer_name, items, total FROM orders"
        ).fetchone()

    assert row is not None
    assert row[0] == "Alice"
    assert row[2] == 25.5