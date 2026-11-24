from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RefundRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    order_id: int = Field(gt=0)
    reason: str = Field(min_length=10)
    refund_amount: Decimal = Field(gt=0)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        if value.isdigit():
            raise ValueError("reason не должен состоять только из цифр")
        return value