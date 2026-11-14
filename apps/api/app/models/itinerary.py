from typing import List, Optional, TYPE_CHECKING
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Date, ForeignKey, JSON, Boolean
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.trip import Trip


class ItineraryDay(Base, TimestampMixin):
    __tablename__ = "itinerary_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id"), nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    theme_title: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    weather_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="itinerary_days")
    activities: Mapped[List["Activity"]] = relationship("Activity", back_populates="itinerary_day", cascade="all, delete-orphan")


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    itinerary_day_id: Mapped[str] = mapped_column(String(36), ForeignKey("itinerary_days.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:mm
    end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)    # HH:mm
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_cost_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    booking_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    booking_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provenance_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    itinerary_day: Mapped["ItineraryDay"] = relationship("ItineraryDay", back_populates="activities")


class AccommodationOption(Base, TimestampMixin):
    __tablename__ = "accommodation_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="hotel", nullable=False)
    check_in_date: Mapped[date] = mapped_column(Date, nullable=False)
    check_out_date: Mapped[date] = mapped_column(Date, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    provenance_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class TransportationOption(Base, TimestampMixin):
    __tablename__ = "transportation_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(30), nullable=False)  # flight, train, drive, bus
    departure_time: Mapped[str] = mapped_column(String(30), nullable=False)
    arrival_time: Mapped[str] = mapped_column(String(30), nullable=False)
    origin_name: Mapped[str] = mapped_column(String(200), nullable=False)
    destination_name: Mapped[str] = mapped_column(String(200), nullable=False)
    carrier_or_provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_cost_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    provenance_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
