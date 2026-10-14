
"""
ELTC — Module 04: Integrated Shipment Planner Tests

Test IDs:
    SP-01: Successful end-to-end shipment plan
    SP-02: Invalid cargo input
    SP-03: No compatible wagon
    SP-04: Unknown origin station
    SP-05: Unreachable destination
    SP-06: Custom freight rates
    SP-07: Cost breakdown consistency
"""

from backend.shipment_planner import plan_shipment
from backend.wagon_selection import Cargo
from backend.freight_cost import FreightRates


# ============================================================
# 01. REUSABLE TEST INPUT
# ============================================================

def valid_cargo():
    return Cargo(
        commodity_type="agricultural",
        weight_tonnes=40.0,
        volume_m3=50.0,
        loading_method="top_loading",
    )


# ============================================================
# 02. END-TO-END SUCCESS
# ============================================================

def test_SP_01_successful_shipment_plan():
    result = plan_shipment(
        "Delhi",
        "Mumbai",
        valid_cargo(),
    )

    assert result["status"] == "success"
    assert result["shipment"]["origin"] == "Delhi"
    assert result["shipment"]["destination"] == "Mumbai"

    assert result["wagon_options"]
    assert result["wagon_options"][0]["wagon_name"] == "Open Wagon"

    assert result["route"]["status"] == "success"
    assert result["route"]["path"] == [
        "Delhi",
        "Jaipur",
        "Ahmedabad",
        "Mumbai",
    ]

    assert result["freight_estimate"]["total_cost_inr"] == 86300.0
    assert result["data_status"] == "ILLUSTRATIVE_DEMO_ONLY"


# ============================================================
# 03. INVALID CARGO
# ============================================================

def test_SP_02_invalid_cargo():
    cargo = Cargo(
        commodity_type="agricultural",
        weight_tonnes=-10,
        volume_m3=50,
        loading_method="top_loading",
    )

    result = plan_shipment("Delhi", "Mumbai", cargo)

    assert result["status"] == "invalid_input"
    assert result["route"] is None
    assert result["freight_estimate"] is None
    assert result["errors"]


# ============================================================
# 04. NO FEASIBLE WAGON
# ============================================================

def test_SP_03_no_compatible_wagon():
    cargo = Cargo(
        commodity_type="unconfigured_commodity",
        weight_tonnes=10,
        volume_m3=10,
        loading_method="top_loading",
    )

    result = plan_shipment("Delhi", "Mumbai", cargo)

    assert result["status"] == "no_feasible_wagon"
    assert result["wagon_options"] == []
    assert result["route"] is None


# ============================================================
# 05. INVALID OR UNAVAILABLE ROUTE
# ============================================================

def test_SP_04_unknown_origin():
    result = plan_shipment(
        "Unknown Station",
        "Mumbai",
        valid_cargo(),
    )

    assert result["status"] == "invalid_route_input"
    assert result["freight_estimate"] is None
    assert result["errors"]


def test_SP_05_unreachable_destination():
    disconnected_network = {
        "Delhi": {},
        "Mumbai": {},
    }

    result = plan_shipment(
        "Delhi",
        "Mumbai",
        valid_cargo(),
        network=disconnected_network,
    )

    assert result["status"] == "no_route"
    assert result["route"]["status"] == "no_route"
    assert result["freight_estimate"] is None


# ============================================================
# 06. CUSTOM RATES AND COST CONSISTENCY
# ============================================================

def test_SP_06_custom_freight_rates():
    rates = FreightRates(
        rate_per_tonne_km=2.0,
        loading_per_tonne=50.0,
        unloading_per_tonne=25.0,
        handling_charge=100.0,
    )

    result = plan_shipment(
        "Delhi",
        "Mumbai",
        valid_cargo(),
        rates=rates,
    )

    assert result["status"] == "success"
    assert result["freight_estimate"]["total_cost_inr"] == 107900.0


def test_SP_07_cost_breakdown_matches_total():
    result = plan_shipment(
        "Delhi",
        "Mumbai",
        valid_cargo(),
    )

    breakdown = result["freight_estimate"]["cost_breakdown"]

    assert round(sum(breakdown.values()), 2) == (
        result["freight_estimate"]["total_cost_inr"]
    )
