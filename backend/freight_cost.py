
"""
ELTC — Efficient Loading and Transportation of New Commodities
Module 03: Freight Cost Estimation

Purpose:
    Estimate shipment cost using configurable demo rates.

IMPORTANT:
    Rates in this module are illustrative, not official Indian
    Railways tariffs. This module does not generate a railway quote.
"""

from dataclasses import dataclass
import math


# ============================================================
# 01. CONFIGURABLE DEMO RATES
# ============================================================
# Replace these with verified rates before operational use.
# Monetary values are illustrative INR amounts.

@dataclass(frozen=True)
class FreightRates:
    rate_per_tonne_km: float = 1.50
    loading_per_tonne: float = 100.00
    unloading_per_tonne: float = 80.00
    handling_charge: float = 500.00


DEFAULT_RATES = FreightRates()


# ============================================================
# 02. INPUT VALIDATION
# ============================================================

def validate_cost_inputs(
    weight_tonnes,
    distance_km,
    rates,
):
    """Validate shipment quantities and configured rates."""

    errors = []

    for field_name, value in (
        ("Cargo weight", weight_tonnes),
        ("Distance", distance_km),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            errors.append(
                f"{field_name} must be a finite number."
            )
        elif value <= 0:
            errors.append(
                f"{field_name} must be greater than zero."
            )

    if not isinstance(rates, FreightRates):
        errors.append("Rates must be a FreightRates object.")
        return errors

    for field_name, value in (
        ("Rate per tonne-km", rates.rate_per_tonne_km),
        ("Loading rate", rates.loading_per_tonne),
        ("Unloading rate", rates.unloading_per_tonne),
        ("Handling charge", rates.handling_charge),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            errors.append(
                f"{field_name} must be a finite, "
                "non-negative number."
            )

    return errors


# ============================================================
# 03. FREIGHT COST CALCULATOR
# ============================================================

def estimate_freight_cost(
    weight_tonnes,
    distance_km,
    rates=None,
):
    """
    Estimate a shipment's cost using illustrative rates.

    Formula:
        Transportation = weight x distance x rate per tonne-km
        Loading        = weight x loading rate
        Unloading      = weight x unloading rate
        Total          = sum of all components

    Returns a structured result with a visible cost breakdown.
    """

    if rates is None:
        rates = DEFAULT_RATES

    errors = validate_cost_inputs(
        weight_tonnes,
        distance_km,
        rates,
    )

    if errors:
        return {
            "status": "invalid_input",
            "data_status": "ILLUSTRATIVE_DEMO_ONLY",
            "errors": errors,
            "cost_breakdown": {},
            "total_cost_inr": None,
        }

    transportation_cost = (
        weight_tonnes
        * distance_km
        * rates.rate_per_tonne_km
    )

    loading_cost = (
        weight_tonnes * rates.loading_per_tonne
    )

    unloading_cost = (
        weight_tonnes * rates.unloading_per_tonne
    )

    handling_cost = rates.handling_charge

    total_cost = (
        transportation_cost
        + loading_cost
        + unloading_cost
        + handling_cost
    )

    breakdown = {
        "transportation_cost_inr": round(
            transportation_cost, 2
        ),
        "loading_cost_inr": round(loading_cost, 2),
        "unloading_cost_inr": round(unloading_cost, 2),
        "handling_cost_inr": round(handling_cost, 2),
    }

    return {
        "status": "success",
        "data_status": "ILLUSTRATIVE_DEMO_ONLY",
        "weight_tonnes": weight_tonnes,
        "distance_km": distance_km,
        "cost_breakdown": breakdown,
        "total_cost_inr": round(total_cost, 2),
        "assumptions": [
            "Illustrative rates only; not official railway tariffs.",
            "No taxes, surcharges, or other unconfigured charges included.",
            "Actual charges depend on applicable rules and shipment details.",
        ],
    }


# ============================================================
# 04. MANUAL DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    sample_weight = 20.0
    sample_distance = 500.0

    result = estimate_freight_cost(
        weight_tonnes=sample_weight,
        distance_km=sample_distance,
    )

    print("\nELTC — Freight Cost Estimation")
    print("=" * 42)
    print(f"Cargo weight: {sample_weight} tonnes")
    print(f"Distance: {sample_distance} km")
    print(f"Status: {result['status']}")

    if result["status"] == "success":
        print("\nIllustrative cost breakdown:")

        for component, amount in (
            result["cost_breakdown"].items()
        ):
            readable_name = (
                component
                .replace("_inr", "")
                .replace("_", " ")
                .title()
            )
            print(f"{readable_name}: Rs. {amount:,.2f}")

        print("-" * 42)
        print(
            f"Estimated total: "
            f"Rs. {result['total_cost_inr']:,.2f}"
        )
        print("\nAssumptions:")
        for assumption in result["assumptions"]:
            print(f"- {assumption}")

    else:
        print("Errors:")
        for error in result["errors"]:
            print(f"- {error}")
