
"""
ELTC — Automated Wagon Selection Tests
Test module 01

Run from the repository root:
python -m pytest backend/tests -v
"""

import pytest

from backend.wagon_selection import (
    Cargo,
    Wagon,
    evaluate_wagon,
    recommend_wagons,
    validate_cargo,
)


# 01. REUSABLE TEST FIXTURES
@pytest.fixture
def test_wagon():
    return Wagon(
        wagon_id="TEST_OPEN",
        name="Test Open Wagon",
        max_payload_tonnes=60.0,
        usable_volume_m3=75.0,
        commodity_types=("bulk", "agricultural"),
        loading_methods=("top_loading",),
    )


@pytest.fixture
def valid_cargo():
    return Cargo(
        commodity_type="agricultural",
        weight_tonnes=40.0,
        volume_m3=50.0,
        loading_method="top_loading",
    )


# TC-01: Valid cargo passes validation.
def test_TC_01_valid_cargo(valid_cargo):
    assert validate_cargo(valid_cargo) == []


# TC-02: Zero or negative weight and volume are rejected.
@pytest.mark.parametrize(
    ("weight", "volume"),
    [(0, 10), (-5, 10), (10, 0), (10, -5)],
)
def test_TC_02_invalid_dimensions(weight, volume):
    cargo = Cargo("agricultural", weight, volume, "top_loading")
    result = recommend_wagons(cargo)

    assert result["status"] == "invalid_input"
    assert result["recommendations"] == []


# TC-03: Payload above the configured limit is rejected.
def test_TC_03_payload_limit(test_wagon):
    cargo = Cargo("agricultural", 61, 50, "top_loading")
    result = evaluate_wagon(cargo, test_wagon)

    assert not result["feasible"]
    assert "Cargo exceeds configured payload limit." in result["reasons"]


# TC-04: Volume above the configured limit is rejected.
def test_TC_04_volume_limit(test_wagon):
    cargo = Cargo("agricultural", 40, 76, "top_loading")
    result = evaluate_wagon(cargo, test_wagon)

    assert not result["feasible"]
    assert "Cargo exceeds configured usable volume." in result["reasons"]


# TC-05: An unconfigured commodity is rejected.
def test_TC_05_commodity_compatibility(test_wagon):
    cargo = Cargo("container", 20, 30, "top_loading")
    result = evaluate_wagon(cargo, test_wagon)

    assert not result["feasible"]
    assert any("Commodity compatibility" in reason
               for reason in result["reasons"])


# TC-06: An unsupported loading method is rejected.
def test_TC_06_loading_method(test_wagon):
    cargo = Cargo("agricultural", 20, 30, "crane_loading")
    result = evaluate_wagon(cargo, test_wagon)

    assert not result["feasible"]
    assert any("Loading method" in reason
               for reason in result["reasons"])


# TC-07: Cargo exactly at configured limits is accepted.
def test_TC_07_exact_limits(test_wagon):
    cargo = Cargo("agricultural", 60, 75, "top_loading")
    result = evaluate_wagon(cargo, test_wagon)

    assert result["feasible"]
    assert result["weight_utilization_percent"] == 100
    assert result["volume_utilization_percent"] == 100


# TC-08: Recommendations are ordered by utilization.
def test_TC_08_recommendation_ranking(valid_cargo):
    result = recommend_wagons(valid_cargo)
    recommendations = result["recommendations"]

    assert result["status"] == "success"

    scores = [
        (
            item["weight_utilization_percent"]
            + item["volume_utilization_percent"]
        ) / 2
        for item in recommendations
    ]

    assert scores == sorted(scores, reverse=True)


# TC-09: All recommended wagons pass the configured checks.
def test_TC_09_all_recommendations_feasible(valid_cargo):
    result = recommend_wagons(valid_cargo)

    assert all(
        item["feasible"]
        for item in result["recommendations"]
    )


# TC-10: Blank commodity or loading method is rejected.
@pytest.mark.parametrize(
    ("commodity", "method"),
    [("", "top_loading"), ("agricultural", "")],
)
def test_TC_10_required_fields(commodity, method):
    cargo = Cargo(commodity, 20, 30, method)
    result = recommend_wagons(cargo)

    assert result["status"] == "invalid_input"
    assert result["recommendations"] == []
