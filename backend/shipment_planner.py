
"""
ELTC — Efficient Loading and Transportation of New Commodities
Module 04: Integrated Shipment Planner

Combines:
    1. Wagon selection
    2. Minimum-cost route optimization
    3. Illustrative freight cost estimation

IMPORTANT:
    Uses illustrative data. This is not an official Indian Railways
    quotation or a complete operational feasibility assessment.
"""

from backend.wagon_selection import (
    Cargo,
    recommend_wagons,
)
from backend.route_optimization import (
    find_minimum_cost_route,
)
from backend.freight_cost import (
    DEFAULT_RATES,
    FreightRates,
    estimate_freight_cost,
)


# ============================================================
# 01. INTEGRATED SHIPMENT PLANNING
# ============================================================

def plan_shipment(
    origin,
    destination,
    cargo,
    network=None,
    rates=None,
):
    """
    Build a shipment plan using the existing ELTC modules.

    Returns:
        status
        wagon_options
        route
        freight_estimate
        warnings
    """

    # --------------------------------------------------------
    # 01.1 Validate cargo and identify feasible wagons
    # --------------------------------------------------------

    wagon_result = recommend_wagons(cargo)

    if wagon_result["status"] != "success":
        return {
            "status": "invalid_input",
            "wagon_options": [],
            "route": None,
            "freight_estimate": None,
            "errors": wagon_result.get(
                "errors", ["Cargo validation failed."]
            ),
            "warnings": [
                "Illustrative wagon data is not official railway data."
            ],
        }

    if not wagon_result["recommendations"]:
        return {
            "status": "no_feasible_wagon",
            "wagon_options": [],
            "route": None,
            "freight_estimate": None,
            "errors": [
                "No configured wagon satisfies all cargo constraints."
            ],
            "warnings": [
                "Check cargo compatibility and verify actual wagon specifications."
            ],
        }

    # --------------------------------------------------------
    # 01.2 Find the minimum-cost route
    # --------------------------------------------------------

    try:
        route_result = find_minimum_cost_route(
            source=origin,
            destination=destination,
            network=network,
        )
    except ValueError as exc:
        return {
            "status": "invalid_route_input",
            "wagon_options": wagon_result["recommendations"],
            "route": None,
            "freight_estimate": None,
            "errors": [str(exc)],
            "warnings": [],
        }

    if route_result["status"] != "success":
        return {
            "status": "no_route",
            "wagon_options": wagon_result["recommendations"],
            "route": route_result,
            "freight_estimate": None,
            "errors": [
                "No connected route was found for this shipment."
            ],
            "warnings": [],
        }

    # --------------------------------------------------------
    # 01.3 Estimate shipment cost using selected route distance
    # --------------------------------------------------------

    freight_result = estimate_freight_cost(
        weight_tonnes=cargo.weight_tonnes,
        distance_km=route_result["total_distance_km"],
        rates=rates if rates is not None else DEFAULT_RATES,
    )

    if freight_result["status"] != "success":
        return {
            "status": "cost_estimation_failed",
            "wagon_options": wagon_result["recommendations"],
            "route": route_result,
            "freight_estimate": freight_result,
            "errors": freight_result.get(
                "errors", ["Freight cost estimation failed."]
            ),
            "warnings": [],
        }

    # --------------------------------------------------------
    # 01.4 Assemble the integrated result
    # --------------------------------------------------------

    return {
        "status": "success",
        "data_status": "ILLUSTRATIVE_DEMO_ONLY",
        "shipment": {
            "origin": origin,
            "destination": destination,
            "commodity_type": cargo.commodity_type,
            "weight_tonnes": cargo.weight_tonnes,
            "volume_m3": cargo.volume_m3,
            "loading_method": cargo.loading_method,
        },
        "wagon_options": wagon_result["recommendations"],
        "route": route_result,
        "freight_estimate": freight_result,
        "warnings": [
            "Wagon capacities and compatibility are illustrative.",
            "Route costs, distances, and times are illustrative.",
            "Freight rates are not official Indian Railways tariffs.",
            "Route selection minimizes configured route cost, "
            "not necessarily the final freight estimate.",
            "Actual railway feasibility, availability, handling "
            "rules, and applicable charges must be verified.",
        ],
    }


# ============================================================
# 02. MANUAL DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    sample_cargo = Cargo(
        commodity_type="agricultural",
        weight_tonnes=40.0,
        volume_m3=50.0,
        loading_method="top_loading",
    )

    result = plan_shipment(
        origin="Delhi",
        destination="Mumbai",
        cargo=sample_cargo,
    )

    print("\nELTC — Integrated Shipment Planner")
    print("=" * 48)
    print(f"Status: {result['status']}")

    if result["status"] == "success":
        shipment = result["shipment"]
        route = result["route"]
        freight = result["freight_estimate"]

        print(
            f"\nShipment: {shipment['origin']} -> "
            f"{shipment['destination']}"
        )
        print(f"Commodity: {shipment['commodity_type']}")
        print(f"Weight: {shipment['weight_tonnes']} tonnes")

        print("\nFeasible wagon options:")
        for index, wagon in enumerate(
            result["wagon_options"],
            start=1,
        ):
            print(
                f"{index}. {wagon['wagon_name']} | "
                f"Weight utilization: "
                f"{wagon['weight_utilization_percent']}% | "
                f"Volume utilization: "
                f"{wagon['volume_utilization_percent']}%"
            )

        print("\nSelected route:")
        print(" -> ".join(route["path"]))
        print(f"Route cost units: {route['total_cost']}")
        print(f"Distance: {route['total_distance_km']} km")
        print(f"Travel time: {route['total_time_hours']} hours")

        print("\nIllustrative freight estimate:")
        for component, amount in (
            freight["cost_breakdown"].items()
        ):
            print(f"{component}: Rs. {amount:,.2f}")

        print(
            f"Estimated total: "
            f"Rs. {freight['total_cost_inr']:,.2f}"
        )

        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f"- {warning}")

    else:
        print("\nErrors:")
        for error in result.get("errors", []):
            print(f"- {error}")
