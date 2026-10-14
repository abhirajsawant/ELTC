
"""
ELTC — Module 02: Freight Route Optimization Tests

Test IDs:
    RT-01: Minimum-cost route
    RT-02: Route distance and time
    RT-03: Source equals destination
    RT-04: Unknown source
    RT-05: Unknown destination
    RT-06: Unreachable destination
    RT-07: Invalid negative edge cost
    RT-08: Zero-cost connection
    RT-09: Missing edge metric
    RT-10: Default network produces a valid route
"""

import pytest

from backend.route_optimization import (
    RAILWAY_NETWORK,
    find_minimum_cost_route,
)


# ============================================================
# 01. TEST NETWORK
# ============================================================

TEST_NETWORK = {
    "A": {
        "B": {"cost": 2, "distance": 10, "time": 1},
        "C": {"cost": 8, "distance": 20, "time": 3},
    },
    "B": {
        "A": {"cost": 2, "distance": 10, "time": 1},
        "C": {"cost": 3, "distance": 15, "time": 2},
    },
    "C": {
        "A": {"cost": 8, "distance": 20, "time": 3},
        "B": {"cost": 3, "distance": 15, "time": 2},
    },
}


# ============================================================
# 02. ROUTE CORRECTNESS
# ============================================================

def test_RT_01_minimum_cost_route():
    result = find_minimum_cost_route(
        "A", "C", TEST_NETWORK
    )

    assert result["status"] == "success"
    assert result["path"] == ["A", "B", "C"]
    assert result["total_cost"] == 5


def test_RT_02_route_distance_and_time():
    result = find_minimum_cost_route(
        "A", "C", TEST_NETWORK
    )

    assert result["total_distance_km"] == 25
    assert result["total_time_hours"] == 3


def test_RT_03_same_source_and_destination():
    result = find_minimum_cost_route(
        "A", "A", TEST_NETWORK
    )

    assert result["status"] == "success"
    assert result["path"] == ["A"]
    assert result["total_cost"] == 0
    assert result["total_distance_km"] == 0
    assert result["total_time_hours"] == 0


# ============================================================
# 03. INVALID STATION INPUTS
# ============================================================

def test_RT_04_unknown_source():
    with pytest.raises(ValueError, match="Unknown source"):
        find_minimum_cost_route(
            "Unknown", "C", TEST_NETWORK
        )


def test_RT_05_unknown_destination():
    with pytest.raises(ValueError, match="Unknown destination"):
        find_minimum_cost_route(
            "A", "Unknown", TEST_NETWORK
        )


# ============================================================
# 04. DISCONNECTED NETWORK
# ============================================================

def test_RT_06_unreachable_destination():
    disconnected_network = {
        "A": {},
        "B": {},
    }

    result = find_minimum_cost_route(
        "A", "B", disconnected_network
    )

    assert result["status"] == "no_route"
    assert result["path"] == []
    assert result["total_cost"] is None


# ============================================================
# 05. INVALID NETWORK DATA
# ============================================================

def test_RT_07_negative_edge_cost():
    invalid_network = {
        "A": {
            "B": {
                "cost": -1,
                "distance": 10,
                "time": 1,
            }
        },
        "B": {},
    }

    with pytest.raises(ValueError, match="Invalid cost"):
        find_minimum_cost_route(
            "A", "B", invalid_network
        )


def test_RT_08_zero_cost_connection():
    zero_cost_network = {
        "A": {
            "B": {
                "cost": 0,
                "distance": 5,
                "time": 1,
            }
        },
        "B": {
            "A": {
                "cost": 0,
                "distance": 5,
                "time": 1,
            }
        },
    }

    result = find_minimum_cost_route(
        "A", "B", zero_cost_network
    )

    assert result["status"] == "success"
    assert result["path"] == ["A", "B"]
    assert result["total_cost"] == 0


def test_RT_09_missing_edge_metric():
    invalid_network = {
        "A": {
            "B": {"cost": 5, "distance": 10}
        },
        "B": {},
    }

    with pytest.raises(ValueError, match="Invalid time"):
        find_minimum_cost_route(
            "A", "B", invalid_network
        )


# ============================================================
# 06. DEFAULT NETWORK INTEGRATION
# ============================================================

def test_RT_10_default_network_route():
    result = find_minimum_cost_route(
        "Delhi", "Mumbai"
    )

    assert result["status"] == "success"
    assert result["path"][0] == "Delhi"
    assert result["path"][-1] == "Mumbai"
    assert result["total_cost"] == 400
    assert result["data_status"] == "ILLUSTRATIVE_DEMO_ONLY"
    assert all(
        station in RAILWAY_NETWORK
        for station in result["path"]
    )
