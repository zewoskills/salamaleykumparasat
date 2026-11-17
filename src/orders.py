import logging
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)

OrderItem = dict[str, Any]
Order = dict[str, Any]


def _is_valid_customer_name(customer_name: Any) -> bool:
    return isinstance(customer_name, str) and customer_name.strip() != ""


def _is_valid_item(item: Any) -> bool:
    if not isinstance(item, dict):
        return False

    if "price" not in item or "qty" not in item:
        return False

    price = item["price"]
    qty = item["qty"]

    if isinstance(price, bool) or isinstance(qty, bool):
        return False
    if not isinstance(price, (int, float)) or not isinstance(qty, (int, float)):
        return False
    if price < 0:
        return False
    if qty <= 0:
        return False
    return not (isinstance(qty, float) and not qty.is_integer())


def _calculate_total(items: list[OrderItem]) -> float:
    total = 0.0
    for item in items:
        total += float(item["price"]) * float(item["qty"])
    return total


def save_order(order: Order) -> bool:
    logger.info("saving order")

    if not isinstance(order, dict):
        logger.error("error: invalid order")
        return False

    customer_name = order.get("customer_name")
    if not _is_valid_customer_name(customer_name):
        logger.error("error: no name")
        return False

    items = order.get("items")
    if not isinstance(items, list) or not items:
        logger.error("error: no items")
        return False
    if any(not _is_valid_item(item) for item in items):
        logger.error("error: invalid item")
        return False

    total = _calculate_total(items)
    if total != order.get("total"):
        logger.error("error: total mismatch")
        return False

    conn = sqlite3.connect("orders.db")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_name, items, total) VALUES (?, ?, ?)",
            (customer_name, str(items), total),
        )
        conn.commit()
    except sqlite3.Error:
        logger.exception("Failed to save order")
        return False
    finally:
        conn.close()

    logger.info("saved")
    return True