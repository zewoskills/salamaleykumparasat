from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models import RefundRequest


def test_refund_request_accepts_valid_values() -> None:
    request = RefundRequest(
        order_id=1,
        reason="Damaged item",
        refund_amount=Decimal("12.50"),
    )

    assert request.order_id == 1
    assert request.reason == "Damaged item"
    assert request.refund_amount == Decimal("12.50")


@pytest.mark.parametrize(
    ("field", "value"),
    [("reason", "too short"), ("refund_amount", Decimal(0))],
)
def test_refund_request_rejects_invalid_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "order_id": 1,
        "reason": "A valid refund reason",
        "refund_amount": Decimal("12.50"),
    }
    values[field] = value

    with pytest.raises(ValidationError):
        RefundRequest(**values)
