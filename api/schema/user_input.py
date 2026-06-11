from enum import Enum
from pydantic import BaseModel, Field, computed_field


class TransactionType(str, Enum):
    CASH_OUT = "CASH_OUT"
    TRANSFER = "TRANSFER"
    PAYMENT  = "PAYMENT"
    CASH_IN  = "CASH_IN"
    DEBIT    = "DEBIT"


class UserInput(BaseModel):
    type: TransactionType = Field(
        ...,
        description="Transaction type. Fraud only occurs in CASH_OUT and TRANSFER.",
        examples=["CASH_OUT"]
    )
    amount: float = Field(
        ..., ge=0,
        description="Transaction amount in local currency.",
        examples=[187629.11]
    )
    nameOrig: str = Field(
        ..., min_length=1,
        description="Origin account ID (prefix C = customer).",
        examples=["C1231006815"]
    )
    oldbalanceOrg: float = Field(
        ..., ge=0,
        description="Origin account balance before the transaction.",
        examples=[187629.11]
    )
    newbalanceOrig: float = Field(
        ..., ge=0,
        description="Origin account balance after the transaction.",
        examples=[0.0]
    )
    nameDest: str = Field(
        ..., min_length=1,
        description="Destination account ID (prefix C = customer, M = merchant).",
        examples=["C553264065"]
    )
    oldbalanceDest: float = Field(
        ..., ge=0,
        description="Destination account balance before the transaction.",
        examples=[0.0]
    )
    newbalanceDest: float = Field(
        ..., ge=0,
        description="Destination account balance after the transaction.",
        examples=[187629.11]
    )

    # ── Computed features (not exposed in API input, used internally) ─────────

    @computed_field
    @property
    def is_cash_out(self) -> int:
        return int(self.type == TransactionType.CASH_OUT)

    @computed_field
    @property
    def is_transfer(self) -> int:
        return int(self.type == TransactionType.TRANSFER)

    @computed_field
    @property
    def error_balance_orig(self) -> float:
        return self.oldbalanceOrg - self.amount - self.newbalanceOrig

    @computed_field
    @property
    def error_balance_dest(self) -> float:
        return self.oldbalanceDest + self.amount - self.newbalanceDest

    @computed_field
    @property
    def orig_balance_zero_before(self) -> int:
        return int(self.oldbalanceOrg == 0)

    @computed_field
    @property
    def orig_balance_zero_after(self) -> int:
        return int(self.newbalanceOrig == 0)

    @computed_field
    @property
    def dest_balance_zero_before(self) -> int:
        return int(self.oldbalanceDest == 0)

    @computed_field
    @property
    def amount_to_orig_balance(self) -> float:
        return self.amount / (self.oldbalanceOrg + 1)

    @computed_field
    @property
    def amount_to_dest_balance(self) -> float:
        return self.amount / (self.oldbalanceDest + 1)

    @computed_field
    @property
    def balance_change_orig(self) -> float:
        return self.newbalanceOrig - self.oldbalanceOrg

    @computed_field
    @property
    def balance_change_dest(self) -> float:
        return self.newbalanceDest - self.oldbalanceDest

    @computed_field
    @property
    def dest_is_merchant(self) -> int:
        return int(self.nameDest.startswith("M"))

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type":           "CASH_OUT",
                    "amount":         187629.11,
                    "nameOrig":       "C1231006815",
                    "oldbalanceOrg":  187629.11,
                    "newbalanceOrig": 0.0,
                    "nameDest":       "C553264065",
                    "oldbalanceDest": 0.0,
                    "newbalanceDest": 187629.11
                }
            ]
        }
    }