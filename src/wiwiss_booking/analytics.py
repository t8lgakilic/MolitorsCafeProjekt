from __future__ import annotations

from datetime import date

import pandas as pd

from wiwiss_booking.models import Booking, DashboardSummary, ForecastPoint, IncomeStatement


def estimate_income_tax_2026(taxable_income: float) -> float:
    """Simplified German 2026 Grundtabelle estimate for one taxable income amount."""
    x = max(0, int(taxable_income))
    if x <= 12_348:
        tax = 0.0
    elif x <= 17_799:
        y = (x - 12_348) / 10_000
        tax = (914.51 * y + 1_400) * y
    elif x <= 69_878:
        z = (x - 17_799) / 10_000
        tax = (173.10 * z + 2_397) * z + 1_034.80
    elif x <= 277_825:
        tax = 0.42 * x - 11_187.53
    else:
        tax = 0.45 * x - 19_522.28
    return round(max(0.0, tax), 2)


def _bookings_frame(bookings: list[Booking]) -> pd.DataFrame:
    records = [booking.model_dump() for booking in bookings]
    if not records:
        return pd.DataFrame(columns=["booking_date", "amount", "category", "booking_type", "description"])

    df = pd.DataFrame(records)
    df["booking_date"] = pd.to_datetime(df["booking_date"])
    df["amount"] = df["amount"].astype(float)
    df["signed_amount"] = df.apply(
        lambda row: row["amount"] if row["booking_type"] == "income" else -row["amount"],
        axis=1,
    )
    return df


def income_statement(
    bookings: list[Booking],
    start_date: date | None = None,
    end_date: date | None = None,
) -> IncomeStatement:
    df = _bookings_frame(bookings)
    if df.empty:
        return IncomeStatement(
            start_date=start_date,
            end_date=end_date,
            income=0,
            expenses=0,
            profit=0,
            taxable_umsatz=0,
            estimated_income_tax_2026=0,
            by_category=[],
        )

    if start_date:
        df = df[df["booking_date"] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df["booking_date"] <= pd.Timestamp(end_date)]

    income = float(df.loc[df["booking_type"] == "income", "amount"].sum())
    expenses = float(df.loc[df["booking_type"] == "expense", "amount"].sum())
    umsatz_mask = (
        (df["booking_type"] == "income")
        & df["category"].astype(str).str.casefold().str.contains("umsatz", na=False)
    )
    taxable_umsatz = float(df.loc[umsatz_mask, "amount"].sum())
    by_category_df = (
        df.groupby(["category", "booking_type"], as_index=False)["amount"]
        .sum()
        .sort_values(["booking_type", "amount"], ascending=[True, False])
    )

    return IncomeStatement(
        start_date=start_date,
        end_date=end_date,
        income=round(income, 2),
        expenses=round(expenses, 2),
        profit=round(income - expenses, 2),
        taxable_umsatz=round(taxable_umsatz, 2),
        estimated_income_tax_2026=estimate_income_tax_2026(taxable_umsatz),
        by_category=by_category_df.to_dict(orient="records"),
    )


def forecast_profit(bookings: list[Booking], months: int = 3) -> list[ForecastPoint]:
    df = _bookings_frame(bookings)
    if df.empty:
        return []

    monthly = (
        df.set_index("booking_date")["signed_amount"]
        .resample("ME")
        .sum()
        .tail(6)
    )
    if monthly.empty:
        return []

    expected_profit = round(float(monthly.mean()), 2)
    start_month = monthly.index.max() + pd.offsets.MonthEnd(1)
    future_months = pd.date_range(start=start_month, periods=months, freq="ME")
    return [
        ForecastPoint(month=month.strftime("%Y-%m"), expected_profit=expected_profit)
        for month in future_months
    ]


def dashboard_summary(bookings: list[Booking]) -> DashboardSummary:
    df = _bookings_frame(bookings)
    if df.empty:
        return DashboardSummary(
            total_bookings=0,
            average_booking=0,
            largest_expense_category=None,
            best_month=None,
            monthly=[],
            categories=[],
        )

    df["month"] = df["booking_date"].dt.strftime("%Y-%m")
    monthly_df = (
        df.pivot_table(
            index="month",
            columns="booking_type",
            values="amount",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for column in ["income", "expense"]:
        if column not in monthly_df:
            monthly_df[column] = 0.0
    monthly_df["expenses"] = monthly_df["expense"].astype(float)
    monthly_df["income"] = monthly_df["income"].astype(float)
    monthly_df["profit"] = monthly_df["income"] - monthly_df["expenses"]
    monthly_df = monthly_df[["month", "income", "expenses", "profit"]].sort_values("month")

    categories_df = (
        df.groupby(["category", "booking_type"], as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )
    total_by_type = categories_df.groupby("booking_type")["amount"].transform("sum")
    categories_df["share"] = (categories_df["amount"] / total_by_type * 100).round(2)

    expenses_by_category = categories_df[categories_df["booking_type"] == "expense"]
    largest_expense_category = None
    if not expenses_by_category.empty:
        largest_expense_category = str(expenses_by_category.iloc[0]["category"])

    best_month = None
    if not monthly_df.empty:
        best_month = str(monthly_df.sort_values("profit", ascending=False).iloc[0]["month"])

    return DashboardSummary(
        total_bookings=int(len(df)),
        average_booking=round(float(df["amount"].mean()), 2),
        largest_expense_category=largest_expense_category,
        best_month=best_month,
        monthly=monthly_df.round(2).to_dict(orient="records"),
        categories=categories_df.round(2).to_dict(orient="records"),
    )
