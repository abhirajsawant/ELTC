
"""
ELTC — Efficient Loading and Transportation of New Commodities
Module 02: Freight Route Optimization

Purpose:
    Find the minimum-cost route between railway stations using
    Dijkstra's algorithm.

IMPORTANT:
    The network and all edge values are illustrative demo data.
    They are not official Indian Railways route, tariff, or timetable data.
"""

import heapq
import math


# ============================================================
# 01. ILLUSTRATIVE RAILWAY NETWORK
# ============================================================
# Each connection stores:
#   cost       -> illustrative cost units
#   distance   -> illustrative distance in kilometres
#   time       -> illustrative travel time in hours
#
# The network is undirected for this prototype.

RAILWAY_NETWORK = {
    "Delhi": {
        "Jaipur": {
            "cost": 120,
            "distance": 280,
            "time": 5,
        },
        "Bhopal": {
            "cost": 260,
            "distance": 750,
            "time": 12,
        },
    },
    "Jaipur": {
        "Delhi": {
            "cost": 120,
            "distance": 280,
            "time": 5,
        },
        "Ahmedabad": {
            "cost": 150,
            "distance": 540,
            "time": 9,
        },
    },
    "Ahmedabad": {
        "Jaipur": {
            "cost": 150,
            "distance": 540,
            "time": 9,
        },
        "Mumbai": {
            "cost": 130,
            "distance": 490,
            "time": 8,
        },
    },
    "Mumbai": {
        "Ahmedabad": {
            "cost": 130,
            "distance": 490,
            "time": 8,
        },
        "Nagpur": {
            "cost": 210,
            "distance": 830,
            "time": 14,
        },
    },
    "Bhopal": {
        "Delhi": {
            "cost": 260,
            "distance": 750,
            "time": 12,
        },
        "Nagpur": {
            "cost": 100,
            "distance": 350,
            "time": 6,
        },
    },
    "Nagpur": {
        "Bhopal": {
            "cost": 100,
            "distance": 350,
            "time": 6,
        },
        "Mumbai": {
            "cost": 210,
            "distance": 830,
            "time": 14,
        },
    },
}


# ============================================================
# 02. NETWORK VALIDATION
# ============================================================

def validate_network(network):
    """Check that connections and their weights are valid."""

    if not isinstance(network, dict) or not network:
        raise ValueError("Network must be a non-empty dictionary.")

    for station, neighbours in network.items():
        if not isinstance(station, str) or not station.strip():
            raise ValueError("Every station must have a valid name.")

        if not isinstance(neighbours, dict):
            raise ValueError(
                f"Connections for {station} must be a dictionary."
            )

        for neighbour, edge in neighbours.items():
            if neighbour not in network:
                raise ValueError(
                    f"Unknown connected station: {neighbour}"
                )

            if not isinstance(edge, dict):
                raise ValueError(
                    f"Connection {station} -> {neighbour} "
                    "must contain edge data."
                )

            for field in ("cost", "distance", "time"):
                value = edge.get(field)

                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value < 0
                ):
                    raise ValueError(
                        f"Invalid {field} on "
                        f"{station} -> {neighbour}."
                    )


# ============================================================
# 03. DIJKSTRA MINIMUM-COST ROUTING
# ============================================================

def find_minimum_cost_route(
    source,
    destination,
    network=None,
):
    """
    Find the minimum-cost path from source to destination.

    Dijkstra requires non-negative edge costs.

    Returns a dictionary containing:
        status
        path
        total_cost
        total_distance_km
        total_time_hours
    """

    if network is None:
        network = RAILWAY_NETWORK

    validate_network(network)

    if source not in network:
        raise ValueError(f"Unknown source station: {source}")

    if destination not in network:
        raise ValueError(
            f"Unknown destination station: {destination}"
        )

    if source == destination:
        return {
            "status": "success",
            "path": [source],
            "total_cost": 0,
            "total_distance_km": 0,
            "total_time_hours": 0,
            "data_status": "ILLUSTRATIVE_DEMO_ONLY",
        }

    # Priority queue entries: (accumulated cost, current station)
    priority_queue = [(0, source)]

    minimum_cost = {source: 0}
    previous_station = {}
    visited = set()

    while priority_queue:
        current_cost, current_station = heapq.heappop(
            priority_queue
        )

        if current_station in visited:
            continue

        visited.add(current_station)

        if current_station == destination:
            break

        for neighbour, edge in network[current_station].items():
            if neighbour in visited:
                continue

            new_cost = current_cost + edge["cost"]

            if new_cost < minimum_cost.get(
                neighbour, float("inf")
            ):
                minimum_cost[neighbour] = new_cost
                previous_station[neighbour] = current_station

                heapq.heappush(
                    priority_queue,
                    (new_cost, neighbour),
                )

    # No route exists.
    if destination not in minimum_cost:
        return {
            "status": "no_route",
            "path": [],
            "total_cost": None,
            "total_distance_km": None,
            "total_time_hours": None,
            "data_status": "ILLUSTRATIVE_DEMO_ONLY",
        }

    # Reconstruct the selected route.
    path = []
    current_station = destination

    while current_station != source:
        path.append(current_station)
        current_station = previous_station[current_station]

    path.append(source)
    path.reverse()

    # Sum distance and time along the selected route.
    total_distance = 0
    total_time = 0

    for index in range(len(path) - 1):
        start = path[index]
        end = path[index + 1]
        edge = network[start][end]

        total_distance += edge["distance"]
        total_time += edge["time"]

    return {
        "status": "success",
        "path": path,
        "total_cost": minimum_cost[destination],
        "total_distance_km": total_distance,
        "total_time_hours": total_time,
        "data_status": "ILLUSTRATIVE_DEMO_ONLY",
    }


# ============================================================
# 04. MANUAL DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    source = "Delhi"
    destination = "Mumbai"

    result = find_minimum_cost_route(
        source,
        destination,
    )

    print("\nELTC — Freight Route Optimization")
    print("=" * 42)
    print(f"Origin: {source}")
    print(f"Destination: {destination}")
    print(f"Status: {result['status']}")

    if result["status"] == "success":
        print("\nRecommended minimum-cost route:")
        print(" -> ".join(result["path"]))
        print(f"Total cost units: {result['total_cost']}")
        print(
            f"Total distance: "
            f"{result['total_distance_km']} km"
        )
        print(
            f"Illustrative travel time: "
            f"{result['total_time_hours']} hours"
        )

    print("\nNote: Illustrative data only.")
