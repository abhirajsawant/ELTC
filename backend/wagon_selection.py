
"""
ELTC — Efficient Loading and Transportation of New Commodities
Module 01: Wagon Selection

Purpose:
    Validate cargo inputs, evaluate configured wagon constraints,
    and rank feasible wagon options.

IMPORTANT:
    Wagon capacities and compatibility rules are illustrative demo
    data. They are NOT verified official Indian Railways specifications.
"""

from dataclasses import dataclass
import math


# ============================================================
# 01. WAGON DATA MODEL
# ============================================================

@dataclass(frozen=True)
class Wagon:
    wagon_id: str
    name: str
    max_payload_tonnes: float
    usable_volume_m3: float
    commodity_types: tuple[str, ...]
    loading_methods: tuple[str, ...]
    demo_only: bool = True


# ============================================================
# 02. ILLUSTRATIVE WAGON CATALOGUE
# ============================================================
# Replace these example values with verified specifications
# before using the system for real freight recommendations.

WAGONS = [
    Wagon(
        wagon_id="DEMO_OPEN",
        name="Open Wagon",
        max_payload_tonnes=60.0,
        usable_volume_m3=75.0,
        commodity_types=("bulk", "mineral", "agricultural"),
        loading_methods=("top_loading",),
    ),
    Wagon(
        wagon_id="DEMO_COVERED",
        name="Covered Wagon",
        max_payload_tonnes=55.0,
        usable_volume_m3=90.0,
        commodity_types=("agricultural", "packaged", "general"),
        loading_methods=("side_loading", "door_loading"),
    ),
    Wagon(
        wagon_id="DEMO_FLAT",
        name="Flat Wagon",
        max_payload_tonnes=60.0,
        usable_volume_m3=60.0,
        commodity_types=("container", "machinery", "general"),
        loading_methods=("top_loading", "crane_loading"),
    ),
]


# ============================================================
# 03. CARGO DATA MODEL
# ============================================================

@dataclass(frozen=True)
class Cargo:
    commodity_type: str
    weight_tonnes: float
    volume_m3: float
    loading_method: str


# ============================================================
# 04. NUMERIC INPUT VALIDATION
# ============================================================

def validate_cargo(cargo: Cargo) -> list[str]:
    """Validate cargo fields before evaluating wagon options."""

    errors = []

    if not isinstance(cargo.commodity_type, str):
        errors.append("Commodity type must be text.")
    elif not cargo.commodity_type.strip():
        errors.append("Commodity type is required.")

    if not isinstance(cargo.loading_method, str):
        errors.append("Loading method must be text.")
    elif not cargo.loading_method.strip():
        errors.append("Loading method is required.")

    for field_name, value in (
        ("Cargo weight", cargo.weight_tonnes),
        ("Cargo volume", cargo.volume_m3),
    ):
        # Reject booleans, non-numeric values, NaN and infinity.
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            errors.append(f"{field_name} must be a finite number.")
        elif value <= 0:
            errors.append(
                f"{field_name} must be greater than zero."
            )

    return errors


# ============================================================
# 05. WAGON FEASIBILITY CHECK
# ============================================================

def evaluate_wagon(cargo: Cargo, wagon: Wagon) -> dict:
    """
    Evaluate configured payload, volume, commodity and loading
    constraints for one wagon.

    This does not validate every railway operating requirement.
    """

    errors = validate_cargo(cargo)

    if errors:
        raise ValueError(
            "Invalid cargo: " + "; ".join(errors)
        )

    if (
        not math.isfinite(wagon.max_payload_tonnes)
        or wagon.max_payload_tonnes <= 0
        or not math.isfinite(wagon.usable_volume_m3)
        or wagon.usable_volume_m3 <= 0
    ):
        raise ValueError(
            f"Wagon {wagon.wagon_id} has invalid capacity data."
        )

    weight_utilization = (
        cargo.weight_tonnes / wagon.max_payload_tonnes * 100
    )

    volume_utilization = (
        cargo.volume_m3 / wagon.usable_volume_m3 * 100
    )

    reasons = []

    if cargo.weight_tonnes > wagon.max_payload_tonnes:
        reasons.append(
            "Cargo exceeds configured payload limit."
        )

    if cargo.volume_m3 > wagon.usable_volume_m3:
        reasons.append(
            "Cargo exceeds configured usable volume."
        )

    if (
        cargo.commodity_type.strip().lower()
        not in wagon.commodity_types
    ):
        reasons.append(
            "Commodity compatibility is not configured."
        )

    if (
        cargo.loading_method.strip().lower()
        not in wagon.loading_methods
    ):
        reasons.append(
            "Loading method is not configured."
        )

    return {
        "wagon_id": wagon.wagon_id,
        "wagon_name": wagon.name,
        "feasible": not reasons,
        "weight_utilization_percent": round(
            weight_utilization, 2
        ),
        "volume_utilization_percent": round(
            volume_utilization, 2
        ),
        "reasons": reasons,
        "demo_only": wagon.demo_only,
    }


# ============================================================
# 06. WAGON RECOMMENDATION ENGINE
# ============================================================

def recommend_wagons(cargo: Cargo) -> dict:
    """
    Return feasible wagons ranked by average weight and volume
    utilization, along with rejected alternatives.

    Ranking is a demonstration heuristic, NOT cost optimization.
    """

    errors = validate_cargo(cargo)

    if errors:
        return {
            "status": "invalid_input",
            "data_status": "ILLUSTRATIVE_DEMO_ONLY",
            "errors": errors,
            "recommendations": [],
            "rejected_options": [],
        }

    results = [
        evaluate_wagon(cargo, wagon)
        for wagon in WAGONS
    ]

    feasible = [
        result
        for result in results
        if result["feasible"]
    ]

    rejected = [
        result
        for result in results
        if not result["feasible"]
    ]

    # Higher average utilization ranks first.
    feasible.sort(
        key=lambda item: (
            item["weight_utilization_percent"]
            + item["volume_utilization_percent"]
        ) / 2,
        reverse=True,
    )

    return {
        "status": "success",
        "data_status": "ILLUSTRATIVE_DEMO_ONLY",
        "message": (
            "Results use illustrative wagon data and configured "
            "constraints. Verify applicable Indian Railways "
            "specifications and handling rules before operational use."
        ),
        "recommendations": feasible,
        "rejected_options": rejected,
    }


# ============================================================
# 07. MANUAL DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    # Example cargo: agricultural products.
    sample_cargo = Cargo(
        commodity_type="agricultural",
        weight_tonnes=40.0,
        volume_m3=50.0,
        loading_method="top_loading",
    )

    result = recommend_wagons(sample_cargo)

    print("\nELTC — Wagon Selection Prototype")
    print("=" * 42)
    print(f"Commodity: {sample_cargo.commodity_type}")
    print(f"Weight: {sample_cargo.weight_tonnes} tonnes")
    print(f"Volume: {sample_cargo.volume_m3} m³")
    print(f"Status: {result['status']}")

    if result["status"] == "invalid_input":
        print("\nInput errors:")
        for error in result["errors"]:
            print(f"- {error}")

    else:
        print("\nFeasible wagon options:")

        for index, wagon in enumerate(
            result["recommendations"],
            start=1,
        ):
            print(
                f"{index}. {wagon['wagon_name']} | "
                f"Weight utilization: "
                f"{wagon['weight_utilization_percent']}% | "
                f"Volume utilization: "
                f"{wagon['volume_utilization_percent']}%"
            )

        print("\nRejected options:")

        if not result["rejected_options"]:
            print("None")

        for wagon in result["rejected_options"]:
            print(
                f"- {wagon['wagon_name']}: "
                f"{', '.join(wagon['reasons'])}"
            )

    print("\nNote: Demo data only; not an official railway assessment.")
