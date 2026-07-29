from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


BookingType = Literal["income", "expense"]
UserRole = Literal["admin", "user"]


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: SecretStr = Field(min_length=4, max_length=80)
    role: UserRole = "user"

    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, value: str) -> str:
        return str(value).strip().lower()


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    created_at: datetime


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: SecretStr = Field(min_length=4, max_length=80)

    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, value: str) -> str:
        return str(value).strip().lower()


class BookingCreate(BaseModel):
    booking_date: date
    amount: Decimal = Field(gt=0, decimal_places=2)
    category: str = Field(min_length=2, max_length=60)
    booking_type: BookingType
    description: str = Field(default="Keine Beschreibung", min_length=2, max_length=200)

    @field_validator("category", mode="before")
    @classmethod
    def clean_category(cls, value: str) -> str:
        return str(value).strip()

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value: str | None) -> str:
        cleaned = str(value or "").strip()
        return cleaned or "Keine Beschreibung"


class Booking(BookingCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class RecurringBookingCreate(BaseModel):
    booking: BookingCreate
    months: int = Field(ge=2, le=24)


class IncomeStatement(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    income: float
    expenses: float
    profit: float
    taxable_umsatz: float
    estimated_income_tax_2026: float
    by_category: list[dict[str, float | str]]


class ForecastPoint(BaseModel):
    month: str
    expected_profit: float


class MonthlySummary(BaseModel):
    month: str
    income: float
    expenses: float
    profit: float


class CategorySummary(BaseModel):
    category: str
    booking_type: BookingType
    amount: float
    share: float


class DashboardSummary(BaseModel):
    total_bookings: int
    average_booking: float
    largest_expense_category: str | None
    best_month: str | None
    monthly: list[MonthlySummary]
    categories: list[CategorySummary]
