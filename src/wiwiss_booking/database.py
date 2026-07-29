from __future__ import annotations

import os
import hashlib
import secrets
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Date, DateTime, Integer, Numeric, String, create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from wiwiss_booking.models import Booking, BookingCreate, LoginRequest, User, UserCreate


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


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(20), default="user", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def _hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), password_salt.encode("utf-8"), 120_000)
    return f"{password_salt}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, _ = stored_hash.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(_hash_password(password, salt), stored_hash)


DEFAULT_USERS = {
    "kai": "user",
    "rüdiger": "user",
    "tah": "user",
    "güler": "user",
    "yıldız": "user",
    "admin": "admin",
}
DEFAULT_PASSWORD = "cafe2026"
LEGACY_DEFAULT_USERS = {"mitarbeiter"}


def _sync_default_users(session: Session) -> None:
    for username, role in DEFAULT_USERS.items():
        row = session.scalars(select(UserRow).where(UserRow.username == username)).first()
        if row is None:
            session.add(UserRow(username=username, password_hash=_hash_password(DEFAULT_PASSWORD), role=role))
        else:
            row.password_hash = _hash_password(DEFAULT_PASSWORD)
            row.role = role

    for username in LEGACY_DEFAULT_USERS:
        row = session.scalars(select(UserRow).where(UserRow.username == username)).first()
        if row is not None:
            session.delete(row)

    session.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        _sync_default_users(session)
        rows = session.scalars(select(BookingRow)).all()
        changed = False
        for row in rows:
            if not row.description or not row.description.strip():
                row.description = "Keine Beschreibung"
                changed = True
        if changed:
            session.commit()


def create_user(user: UserCreate) -> User:
    with SessionLocal() as session:
        row = UserRow(
            username=user.username,
            password_hash=_hash_password(user.password.get_secret_value()),
            role=user.role,
        )
        session.add(row)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError("Benutzername ist bereits vergeben.") from error
        session.refresh(row)
        return User.model_validate(row)


def list_users() -> list[User]:
    with SessionLocal() as session:
        rows = session.scalars(select(UserRow).order_by(UserRow.username.asc())).all()
        return [User.model_validate(row) for row in rows]


def authenticate_user(login: LoginRequest) -> User | None:
    with SessionLocal() as session:
        row = session.scalars(select(UserRow).where(UserRow.username == login.username)).first()
        if row is None:
            return None
        if not _verify_password(login.password.get_secret_value(), row.password_hash):
            return None
        return User.model_validate(row)


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
