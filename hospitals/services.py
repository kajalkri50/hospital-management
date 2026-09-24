"""
Hospital discovery: Haversine distance, filtering, emergency nearest ranking.
"""

from __future__ import annotations

import math
from typing import Any

from django.db.models import QuerySet

from .models import Hospital


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two WGS84 points in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1 - a)))
    return r * c


def annotate_hospitals_with_distance(
    hospitals: QuerySet[Hospital],
    lat: float,
    lng: float,
) -> list[dict[str, Any]]:
    """Evaluate queryset and attach `distance_km` for sorting/display."""
    out: list[dict[str, Any]] = []
    for h in hospitals:
        d = haversine_km(lat, lng, float(h.latitude), float(h.longitude))
        out.append({"hospital": h, "distance_km": round(d, 2)})
    out.sort(key=lambda x: x["distance_km"])
    return out


def filter_hospitals(
    *,
    department: str | None = None,
    min_rating: float | None = None,
    emergency_only: bool | None = None,
    min_general_beds: int | None = None,
) -> QuerySet[Hospital]:
    qs = Hospital.objects.all().prefetch_related("departments", "resources")
    if department:
        qs = qs.filter(departments__name__iexact=department.strip()).distinct()
    if min_rating is not None:
        qs = qs.filter(rating__gte=min_rating)
    if emergency_only:
        qs = qs.filter(emergency_available=True)
    if min_general_beds is not None:
        qs = qs.filter(resources__general_beds_available__gte=min_general_beds)
    return qs


def nearest_emergency_hospitals(lat: float, lng: float, limit: int = 3) -> list[dict[str, Any]]:
    """Top-N emergency-capable hospitals by distance."""
    qs = Hospital.objects.filter(emergency_available=True)
    ranked = annotate_hospitals_with_distance(qs, lat, lng)
    return ranked[:limit]
