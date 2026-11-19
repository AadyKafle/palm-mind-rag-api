import datetime as dt

from sqlalchemy import Date, DateTime, Integer, String, Time, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(10))
    chunking_strategy: Mapped[str] = mapped_column(String(20))
    chunk_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class BookingRecord(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    interview_date: Mapped[dt.date] = mapped_column(Date)
    interview_time: Mapped[dt.time] = mapped_column(Time)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )