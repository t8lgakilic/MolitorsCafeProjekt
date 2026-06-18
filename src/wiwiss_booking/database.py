from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Date, DateTime, Integer, Numeric, String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from wiwiss_booking.models import Booking, BookingCreate


def _default_database_url() -> str:
    db_path = Path(os.getenv("WIWISS_DB_PATH", "data/bookings.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


DATABASE_URL = os.getenv("WIWISS_DATABASE_URL", _default_database_url())
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class BookingRow(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_date: Mapped[datetime.date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(60), index=True)
    booking_type: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        rows = session.scalars(select(BookingRow)).all()
        changed = False
        for row in rows:
            if not row.description or not row.description.strip():
                row.description = "Keine Beschreibung"
                changed = True
        if changed:
            session.commit()


def create_booking(booking: BookingCreate) -> Booking:
    with SessionLocal() as session:
        row = BookingRow(**booking.model_dump())
        session.add(row)
        session.commit()
        session.refresh(row)
        return Booking.model_validate(row)


def create_bookings(bookings: list[BookingCreate]) -> list[Booking]:
    with SessionLocal() as session:
        rows = [BookingRow(**booking.model_dump()) for booking in bookings]
        session.add_all(rows)
        session.commit()
        for row in rows:
            session.refresh(row)
        return [Booking.model_validate(row) for row in rows]


def list_bookings() -> list[Booking]:
    with SessionLocal() as session:
        rows = session.scalars(select(BookingRow).order_by(BookingRow.id.desc())).all()
        return [Booking.model_validate(row) for row in rows]


def delete_booking(booking_id: int) -> bool:
    with SessionLocal() as session:
        row = session.get(BookingRow, booking_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        offset = 1_000_000
        session.execute(
            text("UPDATE bookings SET id = id + :offset WHERE id > :deleted_id"),
            {"offset": offset, "deleted_id": booking_id},
        )
        session.execute(
            text("UPDATE bookings SET id = id - :shift WHERE id > :offset"),
            {"shift": offset + 1, "offset": offset},
        )
        session.commit()
        return True
