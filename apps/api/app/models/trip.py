from typing import List, Optional, TYPE_CHECKING
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Date, ForeignKey, JSON
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.itinerary import ItineraryDay, AccommodationOption, TransportationOption


class Destination(Base, TimestampMixin):
    __tablename__ = "destinations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    destination_id: Mapped[str] = mapped_column(String(36), ForeignKey("destinations.id"), nullable=False)
    party_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    total_budget_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_budget_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    current_revision_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    creator: Mapped["User"] = relationship("User", back_populates="trips")
    destination: Mapped["Destination"] = relationship("Destination")
    itinerary_days: Mapped[List["ItineraryDay"]] = relationship("ItineraryDay", back_populates="trip", cascade="all, delete-orphan")
    revisions: Mapped[List["TripRevision"]] = relationship("TripRevision", back_populates="trip", cascade="all, delete-orphan")


class TripRevision(Base, TimestampMixin):
    __tablename__ = "trip_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id"), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    change_summary: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_source: Mapped[str] = mapped_column(String(50), nullable=False)
    snapshot_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="revisions")
