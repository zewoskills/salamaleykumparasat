from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0, le=1000)
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class Order(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    order_id: int = Field(gt=0)
    customer_email: str = Field(min_length=3, max_length=254)
    items: list[OrderItem] = Field(min_length=1)

    @field_validator("customer_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("customer_email должен содержать символ '@'")
        return value.lower()