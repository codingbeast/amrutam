# app/core/observability/metrics.py
from prometheus_client import Counter

BOOKING_CREATED = Counter(
    "amrutam_booking_created_total",
    "Total number of bookings created",
)
