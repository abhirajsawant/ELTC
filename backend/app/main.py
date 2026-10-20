import csv
import io
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

# Keep generated local confirmation records inside the backend folder.
BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
BOOKINGS_FILE = BACKEND_DIR / "local_bookings.csv"

app = FastAPI(
    title="Rail Optimizer AI API",
    description="Prototype API for freight route comparisons and booking intent.",
    version="0.1.0",
)

# Change CORS_ORIGINS to your deployed frontend URL before production deployment.
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    # Validate user-entered shipment details before calculating estimates.
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    cargo_type: str = Field(default="General goods", min_length=2, max_length=80)
    weight_tonnes: float = Field(gt=0, le=100000)
    priority: Literal["cost", "time", "reliability", "balanced"] = "balanced"
    wagon_preference: str = Field(default="No preference", max_length=80)

    @field_validator("origin", "destination")
    @classmethod
    def clean_location(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Station or city cannot be blank.")
        return value


class ConfirmRequest(BaseModel):
    # This is user intent only; it does not create a real railway booking.
    shipment: dict
    selected_option: dict


def build_options(request: PlanRequest):
    # DEMO ONLY: replace this synthetic calculation with verified route and rate datasets.
    if request.origin.casefold() == request.destination.casefold():
        raise HTTPException(status_code=422, detail="Origin and destination must be different.")

    key = f"{request.origin.casefold()}->{request.destination.casefold()}"
    seed = sum((i + 1) * ord(char) for i, char in enumerate(key))
    base_distance = 250 + seed % 1450
    weight = request.weight_tonnes

    # Basic illustrative wagon suggestion. Verify all wagon compatibility with official data.
    cargo = request.cargo_type.casefold()
    if any(term in cargo for term in ["coal", "cement", "fertilizer"]):
        wagon = "Open / bulk wagon (verify)"
    elif "grain" in cargo or "food" in cargo:
        wagon = "Covered wagon (verify cargo rules)"
    elif "container" in cargo:
        wagon = "Container flat wagon (verify)"
    else:
        wagon = "General-purpose wagon (verify)"
    if request.wagon_preference != "No preference":
        wagon = f"{request.wagon_preference} (compatibility to verify)"

    profiles = [
        {"name": "Option A · Cost-focused", "factor": 1.00, "speed": 38, "rate": 1.55, "reliability": 0.78, "kind": "Cost-first"},
        {"name": "Option B · Time-focused", "factor": 1.12, "speed": 48, "rate": 1.82, "reliability": 0.82, "kind": "Time-first"},
        {"name": "Option C · Balanced", "factor": 1.05, "speed": 42, "rate": 1.67, "reliability": 0.88, "kind": "Balanced"},
    ]
    options = []
    for profile in profiles:
        distance = int(base_distance * profile["factor"])
        hours = round(distance / profile["speed"] + 8, 1)
        cost = round(distance * weight * profile["rate"])
        options.append({
            "route_name": profile["name"],
            "route_description": "Synthetic corridor estimate; not a live railway route.",
            "distance_km": distance,
            "estimated_cost_inr": cost,
            "estimated_transit_hours": hours,
            "wagon_type": wagon,
            "reliability_score": profile["reliability"],
            "priority_label": request.priority.title() + " priority",
            "explanation": f"{profile['kind']} estimate for {weight:g} tonnes. All figures are illustrative placeholders.",
        })

    # Rank by the user-selected objective. Balanced uses normalized cost/time plus reliability.
    if request.priority == "cost":
        options.sort(key=lambda item: item["estimated_cost_inr"])
    elif request.priority == "time":
        options.sort(key=lambda item: item["estimated_transit_hours"])
    elif request.priority == "reliability":
        options.sort(key=lambda item: item["reliability_score"], reverse=True)
    else:
        max_cost = max(item["estimated_cost_inr"] for item in options) or 1
        max_time = max(item["estimated_transit_hours"] for item in options) or 1
        options.sort(key=lambda item: item["estimated_cost_inr"] / max_cost + item["estimated_transit_hours"] / max_time - item["reliability_score"] * 0.25)

    for rank, option in enumerate(options, 1):
        option["rank"] = rank
    return options


@app.get("/")
def root():
    return {"name": "Rail Optimizer AI API", "status": "running", "notice": "Illustrative prototype estimates only."}


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/plan")
def plan(request: PlanRequest):
    # Return multiple options so the user can compare cost, time, and reliability.
    return {
        "request_id": str(uuid.uuid4()),
        "origin": request.origin,
        "destination": request.destination,
        "is_illustrative": True,
        "notice": "Synthetic estimates only: not an official quote, live route, live traffic report, or confirmed capacity.",
        "options": build_options(request),
    }


@app.post("/api/bookings/confirm")
def confirm(request: ConfirmRequest):
    # Store a local confirmation record; this is not an official transport reservation.
    record = {
        "booking_id": str(uuid.uuid4()),
        "confirmed_at_utc": datetime.now(timezone.utc).isoformat(),
        "origin": request.shipment.get("origin", ""),
        "destination": request.shipment.get("destination", ""),
        "cargo_type": request.shipment.get("cargo_type", ""),
        "weight_tonnes": request.shipment.get("weight_tonnes", ""),
        "selected_route": request.selected_option.get("route_name", ""),
        "estimated_cost_inr": request.selected_option.get("estimated_cost_inr", ""),
        "estimated_transit_hours": request.selected_option.get("estimated_transit_hours", ""),
        "is_real_booking": False,
    }
    BOOKINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    exists = BOOKINGS_FILE.exists()
    with BOOKINGS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(record.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(record)
    return {"status": "confirmed_in_prototype", "booking_id": record["booking_id"], "notice": "No real railway booking was made."}


@app.post("/api/admin/datasets/preview")
async def preview_dataset(file: UploadFile = File(...)):
    # Preview CSV headers and up to ten rows. This does not save data or train a model.
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV preview limit is 5 MB.")
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        columns = reader.fieldnames or []
        rows = []
        for index, row in enumerate(reader):
            if index >= 10:
                break
            rows.append(row)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail="Could not parse this CSV file.") from exc
    return {"filename": file.filename, "columns": columns, "preview_rows": rows, "notice": "Preview only; file not saved and no model trained."}


@app.get("/api/bookings/export")
def export_bookings():
    # Download prototype confirmations as a CSV.
    if not BOOKINGS_FILE.exists():
        raise HTTPException(status_code=404, detail="No prototype confirmations have been recorded.")
    def read_lines():
        with BOOKINGS_FILE.open("r", newline="", encoding="utf-8") as file:
            yield from file
    return StreamingResponse(read_lines(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="prototype-bookings.csv"'})
