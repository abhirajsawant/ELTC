
"""
ELTC — Module 05: HTTP API

Endpoints:
    GET  /api/health
    POST /api/plan

Run from the ELTC project root:
    python -m backend.api
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from backend.shipment_planner import plan_shipment
from backend.wagon_selection import Cargo


# ============================================================
# 01. API CONFIGURATION
# ============================================================

HOST = "127.0.0.1"
PORT = 8000

ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


# ============================================================
# 02. HTTP REQUEST HANDLER
# ============================================================

class ELTCRequestHandler(BaseHTTPRequestHandler):
    """Handle ELTC health checks and shipment planning requests."""

    def send_json(self, status_code, payload):
        response = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")

        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        """Allow browser preflight requests from the local frontend."""

        origin = self.headers.get("Origin", "")

        self.send_response(204)

        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header(
                "Access-Control-Allow-Methods",
                "GET, POST, OPTIONS",
            )
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type",
            )
            self.send_header("Vary", "Origin")

        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "application": "ELTC",
                    "data_status": "ILLUSTRATIVE_DEMO_ONLY",
                },
            )
            return

        self.send_json(
            404,
            {"status": "error", "message": "Endpoint not found."},
        )

    def do_POST(self):
        if self.path != "/api/plan":
            self.send_json(
                404,
                {"status": "error", "message": "Endpoint not found."},
            )
            return

        # Accept JSON only.
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            self.send_json(
                415,
                {
                    "status": "error",
                    "message": "Content-Type must be application/json.",
                },
            )
            return

        # Prevent unexpectedly large request bodies in this prototype.
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0

        if content_length <= 0 or content_length > 100_000:
            self.send_json(
                400,
                {
                    "status": "error",
                    "message": "Request body is empty or too large.",
                },
            )
            return

        try:
            request_data = json.loads(
                self.rfile.read(content_length).decode("utf-8")
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(
                400,
                {
                    "status": "error",
                    "message": "Request body must contain valid JSON.",
                },
            )
            return

        if not isinstance(request_data, dict):
            self.send_json(
                400,
                {
                    "status": "error",
                    "message": "Request body must be a JSON object.",
                },
            )
            return

        # Required fields.
        required_fields = (
            "origin",
            "destination",
            "commodity_type",
            "weight_tonnes",
            "volume_m3",
            "loading_method",
        )

        missing = [
            field
            for field in required_fields
            if field not in request_data
        ]

        if missing:
            self.send_json(
                400,
                {
                    "status": "error",
                    "message": "Required fields are missing.",
                    "missing_fields": missing,
                },
            )
            return

        # Validate text fields before creating Cargo.
        text_fields = (
            "origin",
            "destination",
            "commodity_type",
            "loading_method",
        )

        for field in text_fields:
            value = request_data[field]

            if not isinstance(value, str) or not value.strip():
                self.send_json(
                    400,
                    {
                        "status": "error",
                        "message": f"{field} must be non-empty text.",
                    },
                )
                return

        # Cargo validation is performed by the existing planner.
        cargo = Cargo(
            commodity_type=request_data["commodity_type"],
            weight_tonnes=request_data["weight_tonnes"],
            volume_m3=request_data["volume_m3"],
            loading_method=request_data["loading_method"],
        )

        result = plan_shipment(
            origin=request_data["origin"],
            destination=request_data["destination"],
            cargo=cargo,
        )

        # Invalid cargo or route requests are client errors.
        if result["status"] in {
            "invalid_input",
            "invalid_route_input",
        }:
            self.send_json(400, result)
            return

        # A valid request can still have no feasible wagon or route.
        self.send_json(200, result)

    def log_message(self, format_string, *args):
        """Keep concise request logs in the development terminal."""
        print(
            f"[ELTC API] {self.address_string()} - "
            f"{format_string % args}"
        )


# ============================================================
# 03. START DEVELOPMENT SERVER
# ============================================================

def main():
    server = ThreadingHTTPServer((HOST, PORT), ELTCRequestHandler)

    print("ELTC API is running.")
    print(f"Health check: http://{HOST}:{PORT}/api/health")
    print(f"Shipment endpoint: http://{HOST}:{PORT}/api/plan")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ELTC API...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
