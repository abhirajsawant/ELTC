
"""
ELTC — Module 03: Freight Cost Estimation Tests

Test IDs:
    FC-01: Standard shipment calculation
    FC-02: Zero distance rejected
    FC-03: Zero weight rejected
    FC-04: Negative weight rejected
    FC-05: Negative distance rejected
    FC-06: Custom rates
    FC-07: Zero-valued rates
    FC-08: Invalid negative rate
    FC-09: Non-finite numeric inputs
    FC-10: Invalid rate object
    FC-11: Cost breakdown adds to total
    FC-12: Default rates are used
"""
import math
import pytest

from backend.freight_cost import (
    DEFAULT_RATES,
    FreightRates,
    estimate_freight_cost,
)


# ============================================================
# 01. STANDARD CALCULATION
# ============================================================

def test_FC_01_standard_shipment():
    result = estimate_freight_cost(20, 500)

    assert result["status"] == "success"
    assert result["total_cost_inr"] == 19100.00
    assert result["data_status"] == "ILLUSTRATIVE_DEMO_ONLY"


# ============================================================
# 02. INVALID SHIPMENT DIMENSIONS
# ============================================================

@pytest.mark.parametrize(
    "weight, distance",
    [
        (0, 500),
        (20, 0),
        (-5, 500),
        (20, -10),
    ],
)
def test_FC_02_to_FC_05_invalid_dimensions(weight, distance):
    result = estimate_freight_cost(weight, distance)

    assert result["status"] == "invalid_input"
    assert result["total_cost_inr"] is None
    assert result["errors"]


# ============================================================
# 03. CUSTOM AND ZERO RATES
# ============================================================

def test_FC_06_custom_rates():
    rates = FreightRates(
        rate_per_tonne_km=2,
        loading_per_tonne=50,
        unloading_per_tonne=25,
        handling_charge=100,
    )

    result = estimate_freight_cost(10, 100, rates)

    assert result["status"] == "success"
    assert result["cost_breakdown"]["transportation_cost_inr"] == 2000
    assert result["cost_breakdown"]["loading_cost_inr"] == 500
    assert result["cost_breakdown"]["unloading_cost_inr"] == 250
    assert result["cost_breakdown"]["handling_cost_inr"] == 100
    assert result["total_cost_inr"] == 2850


def test_FC_07_zero_valued_rates():
    rates = FreightRates(0, 0, 0, 0)

    result = estimate_freight_cost(10, 100, rates)

    assert result["status"] == "success"
    assert result["total_cost_inr"] == 0


def test_FC_08_negative_rate_rejected():
    rates = FreightRates(
        rate_per_tonne_km=-1,
        loading_per_tonne=50,
        unloading_per_tonne=25,
        handling_charge=100,
    )

    result = estimate_freight_cost(10, 100, rates)

    assert result["status"] == "invalid_input"
    assert result["total_cost_inr"] is None
    assert any("non-negative" in error for error in result["errors"])


# ============================================================
# 04. NUMERIC INPUT VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "weight, distance",
    [
        (float("nan"), 100),
        (10, float("inf")),
        (True, 100),
        (10, False),
    ],
)
def test_FC_09_non_finite_or_boolean_inputs(weight, distance):
    result = estimate_freight_cost(weight, distance)

    assert result["status"] == "invalid_input"
    assert result["total_cost_inr"] is None


def test_FC_10_invalid_rate_object():
    result = estimate_freight_cost(10, 100, rates={})

    assert result["status"] == "invalid_input"
    assert result["total_cost_inr"] is None


# ============================================================
# 05. COST BREAKDOWN CONSISTENCY
# ============================================================

def test_FC_11_breakdown_matches_total():
    result = estimate_freight_cost(20, 500)

    breakdown_total = sum(
        result["cost_breakdown"].values()
    )

    assert math.isclose(
        breakdown_total,
        result["total_cost_inr"],
        abs_tol=0.01,
    )


def test_FC_12_default_rates_are_used():
    result = estimate_freight_cost(20, 500)

    assert result["status"] == "success"
    assert result["total_cost_inr"] == 19100.00

    expected_transport = (
        20 * 500 * DEFAULT_RATES.rate_per_tonne_km
    )

    assert (
        result["cost_breakdown"]["transportation_cost_inr"]
        == expected_transport
    )
