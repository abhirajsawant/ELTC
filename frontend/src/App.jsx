
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/plan";

const INITIAL_FORM = {
  origin: "Delhi",
  destination: "Mumbai",
  commodity_type: "agricultural",
  weight_tonnes: "40",
  volume_m3: "50",
  loading_method: "top_loading",
};

const STATIONS = [
  "Delhi",
  "Jaipur",
  "Ahmedabad",
  "Bhopal",
  "Nagpur",
  "Mumbai",
];

function formatCurrency(value) {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}


function StationRoute({ path }) {
  if (!path?.length) {
    return (
      <div className="empty-route">
        Your optimized route will appear here.
      </div>
    );
  }

  return (
    <div className="route-visualization">
      <div className="route-track">
        {path.map((station, index) => {
          const isOrigin = index === 0;
          const isDestination = index === path.length - 1;
          const type = isOrigin
            ? "origin"
            : isDestination
              ? "destination"
              : "transfer";

          return (
            <div
              className={`route-stop route-stop-${type}`}
              key={`${station}-${index}`}
            >
              <div
                className={`route-stop-marker marker-${type}`}
                aria-label={
                  isOrigin
                    ? "Origin station"
                    : isDestination
                      ? "Destination station"
                      : "Transfer station"
                }
                title={
                  isOrigin
                    ? "Origin"
                    : isDestination
                      ? "Destination"
                      : "Transfer station"
                }
              >
                {isOrigin ? (
                  <span>▲</span>
                ) : isDestination ? (
                  <span>■</span>
                ) : (
                  <span>●</span>
                )}
              </div>

              <div className="route-stop-name">{station}</div>

              <div className="route-stop-role">
                {isOrigin
                  ? "ORIGIN"
                  : isDestination
                    ? "DESTINATION"
                    : "TRANSFER"}
              </div>

              {index < path.length - 1 && (
                <div className="route-connector" aria-hidden="true">
                  <span />
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="route-legend" aria-label="Route symbol legend">
        <span>
          <b className="legend-symbol legend-origin">▲</b>
          Origin
        </span>
        <span>
          <b className="legend-symbol legend-transfer">●</b>
          Transfer station
        </span>
        <span>
          <b className="legend-symbol legend-destination">■</b>
          Destination
        </span>
      </div>
    </div>
  );
}

function App() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    
    const weight = Number(form.weight_tonnes);
    const volume = Number(form.volume_m3);

    if (!form.origin.trim() || !form.destination.trim()) {
      setError("Origin and destination are required.");
      return;
    }

    if (form.origin === form.destination) {
      setError("Choose different origin and destination stations.");
      return;
    }

    if (!Number.isFinite(weight) || weight <= 0) {
      setError("Cargo weight must be greater than zero.");
      return;
    }

    if (!Number.isFinite(volume) || volume <= 0) {
      setError("Cargo volume must be greater than zero.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    if (form.origin === form.destination) {
      setError("Choose different origin and destination stations.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          weight_tonnes: weight,
          volume_m3: volume, 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.message ||
            data.errors?.join(" ") ||
            "The shipment request could not be processed."
        );
        setResult(data.status ? data : null);
        return;
      }

      setResult(data);

      if (data.status !== "success") {
        setError(
          data.errors?.join(" ") ||
            "No complete shipment plan is available for these inputs."
        );
      }
    } catch {
      setError(
        "Could not connect to the ELTC API. Make sure the Python server is running at 127.0.0.1:8000."
      );
    } finally {
      setLoading(false);
    }
  }

  const route = result?.route;
  const freight = result?.freight_estimate;
  const wagons = result?.wagon_options ?? [];
  const successful = result?.status === "success";

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="ELTC home">
          <span className="brand-mark">E</span>
          <span>
            <strong>ELTC</strong>
            <small>Freight intelligence</small>
          </span>
        </a>

        <div className="topbar-right">
          <span className="system-dot" />
          <span>Prototype environment</span>
        </div>
      </header>

      <section className="hero" id="home">
        <div className="eyebrow">
          <span className="eyebrow-line" />
          EFFICIENT LOADING & TRANSPORTATION
        </div>
        <h1>
          Move goods.
          <br />
          <span>Think beyond distance.</span>
        </h1>
        <p>
          Plan a freight journey with wagon suitability, route costs,
          and an illustrative shipment estimate in one place.
        </p>
      </section>

      <section className="workspace">
        <form className="planner-panel" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <div>
              <span className="section-index">01 / SHIPMENT</span>
              <h2>Plan your cargo</h2>
            </div>
            <span className="panel-icon">↗</span>
          </div>

          <div className="field-grid">
            <label className="field">
              <span>Origin station</span>
              <select
                name="origin"
                value={form.origin}
                onChange={updateField}
              >
                {STATIONS.map((station) => (
                  <option key={station} value={station}>
                    {station}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Destination station</span>
              <select
                name="destination"
                value={form.destination}
                onChange={updateField}
              >
                {STATIONS.map((station) => (
                  <option key={station} value={station}>
                    {station}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Commodity type</span>
              <select
                name="commodity_type"
                value={form.commodity_type}
                onChange={updateField}
              >
                <option value="agricultural">Agricultural</option>
                <option value="bulk">Bulk</option>
                <option value="mineral">Mineral</option>
                <option value="packaged">Packaged goods</option>
                <option value="general">General goods</option>
                <option value="container">Container</option>
                <option value="machinery">Machinery</option>
              </select>
            </label>

            <label className="field">
              <span>Loading method</span>
              <select
                name="loading_method"
                value={form.loading_method}
                onChange={updateField}
              >
                <option value="top_loading">Top loading</option>
                <option value="side_loading">Side loading</option>
                <option value="door_loading">Door loading</option>
                <option value="crane_loading">Crane loading</option>
              </select>
            </label>

            <label className="field">
              <span>Cargo weight (tonnes)</span>
              <input
                name="weight_tonnes"
                type="number"
                min="0.01"
                step="any"
                value={form.weight_tonnes}
                onChange={updateField}
                required
              />
            </label>

            <label className="field">
              <span>Cargo volume (m³)</span>
              <input
                name="volume_m3"
                type="number"
                min="0.01"
                step="any"
                value={form.volume_m3}
                onChange={updateField}
                required
              />
            </label>
          </div>

          <button className="plan-button" type="submit" disabled={loading}>
            {loading ? "Calculating route..." : "Generate shipment plan"}
            <span>{loading ? "···" : "→"}</span>
          </button>

          <p className="form-footnote">
            Demo inputs only. Results are estimates, not an official
            railway quotation.
          </p>
        </form>

        <section className="results-panel" aria-live="polite">
          <div className="panel-heading">
            <div>
              <span className="section-index">02 / RESULTS</span>
              <h2>Your freight plan</h2>
            </div>
            <span className="result-status">
              {successful ? "PLAN READY" : "AWAITING INPUT"}
            </span>
          </div>

          {error && (
            <div className="error-message" role="alert">
              <strong>Unable to complete plan</strong>
              <span>{error}</span>
            </div>
          )}

          {!successful && !error && (
            <div className="empty-state">
              <div className="empty-state-symbol">↗</div>
              <h3>A route is waiting to be found.</h3>
              <p>
                Enter your shipment details and generate a plan to
                see the route, wagon options, and cost estimate.
              </p>
            </div>
          )}

          {successful && (
            <>
              <div className="metric-grid">
                <article className="metric-card metric-primary">
                  <span>ESTIMATED SHIPMENT COST</span>
                  <strong>{formatCurrency(freight?.total_cost_inr)}</strong>
                  <small>Illustrative rate model</small>
                </article>
                <article className="metric-card">
                  <span>ROUTE DISTANCE</span>
                  <strong>{route?.total_distance_km?.toLocaleString("en-IN")} km</strong>
                  <small>Demo network distance</small>
                </article>
                <article className="metric-card">
                  <span>TRANSIT TIME</span>
                  <strong>{route?.total_time_hours} hrs</strong>
                  <small>Illustrative travel time</small>
                </article>
              </div>

              <section className="result-section">
                <div className="subsection-heading">
                  <h3>Selected route</h3>
                  <span>{route?.total_cost} cost units</span>
                </div>
                <StationRoute path={route?.path} />
                <p className="route-note">
                  Dijkstra's algorithm minimizes configured route cost;
                  it does not guarantee the lowest real-world freight tariff.
                </p>
              </section>

              <section className="result-section">
                <div className="subsection-heading">
                  <h3>Feasible wagon options</h3>
                  <span>{wagons.length} found</span>
                </div>

                {wagons.length === 0 ? (
                  <p>No configured wagon is feasible for this cargo.</p>
                ) : (
                  <div className="wagon-list">
                    {wagons.map((wagon, index) => (
                      <article className="wagon-item" key={wagon.wagon_id}>
                        <div className="wagon-symbol">▰</div>
                        <div className="wagon-description">
                          <strong>{wagon.wagon_name}</strong>
                          <span>
                            Weight use {wagon.weight_utilization_percent}%
                            {" · "}
                            Volume use {wagon.volume_utilization_percent}%
                          </span>
                        </div>
                        <span className="rank-number">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <section className="result-section">
                <div className="subsection-heading">
                  <h3>Cost breakdown</h3>
                  <span>INR</span>
                </div>
                <div className="cost-list">
                  {Object.entries(freight?.cost_breakdown ?? {}).map(
                    ([key, value]) => (
                      <div className="cost-row" key={key}>
                        <span>
                          {key
                            .replace("_inr", "")
                            .replaceAll("_", " ")
                            .replace(/\b\w/g, (letter) =>
                              letter.toUpperCase()
                            )}
                        </span>
                        <strong>{formatCurrency(value)}</strong>
                      </div>
                    )
                  )}
                  <div className="cost-row cost-total">
                    <span>Total estimate</span>
                    <strong>{formatCurrency(freight?.total_cost_inr)}</strong>
                  </div>
                </div>
              </section>

              <div className="demo-warning">
                <strong>Prototype data notice</strong>
                <p>
                  Wagon specifications, network distances, route costs,
                  travel times, and freight rates are illustrative.
                  Verify official railway requirements before operational use.
                </p>
              </div>
            </>
          )}
        </section>
      </section>

      <footer className="app-footer">
        <span>ELTC · FREIGHT PLANNING PROTOTYPE</span>
        <span>
          <span className="legend-dot" /> Demo data · Not an official quote
        </span>
      </footer>
    </main>
  );
}

export default App;
