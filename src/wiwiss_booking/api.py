from datetime import date

from fastapi import FastAPI, HTTPException, Query
from dateutil.relativedelta import relativedelta

from wiwiss_booking.analytics import dashboard_summary, forecast_profit, income_statement
from wiwiss_booking.database import create_booking, create_bookings, delete_booking, init_db, list_bookings
from wiwiss_booking.models import Booking, BookingCreate, DashboardSummary, ForecastPoint, IncomeStatement, RecurringBookingCreate


app = FastAPI(title="Molitor's Cafe API")


def recurring_description(description: str, current: int, total: int) -> str:
    suffix = f" ({current}/{total})"
    return f"{description[:200 - len(suffix)]}{suffix}"


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/bookings", response_model=Booking)
def add_booking(booking: BookingCreate) -> Booking:
    return create_booking(booking)


@app.post("/bookings/recurring", response_model=list[Booking])
def add_recurring_booking(recurring_booking: RecurringBookingCreate) -> list[Booking]:
    bookings = []
    for month_index in range(recurring_booking.months):
        booking_data = recurring_booking.booking.model_copy(
            update={
                "booking_date": recurring_booking.booking.booking_date + relativedelta(months=month_index),
                "description": recurring_description(
                    recurring_booking.booking.description,
                    month_index + 1,
                    recurring_booking.months,
                ),
            }
        )
        bookings.append(booking_data)
    return create_bookings(bookings)


@app.get("/bookings", response_model=list[Booking])
def get_bookings() -> list[Booking]:
    return list_bookings()


@app.delete("/bookings/{booking_id}")
def remove_booking(booking_id: int) -> dict[str, int | str]:
    deleted = delete_booking(booking_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
    return {"status": "deleted", "id": booking_id}


@app.get("/analytics/income-statement", response_model=IncomeStatement)
def get_income_statement(
    start_date: date | None = None,
    end_date: date | None = None,
) -> IncomeStatement:
    return income_statement(list_bookings(), start_date=start_date, end_date=end_date)


@app.get("/analytics/forecast", response_model=list[ForecastPoint])
def get_forecast(months: int = Query(default=3, ge=1, le=12)) -> list[ForecastPoint]:
    return forecast_profit(list_bookings(), months=months)


@app.get("/analytics/dashboard", response_model=DashboardSummary)
def get_dashboard() -> DashboardSummary:
    return dashboard_summary(list_bookings())
