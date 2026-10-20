import React, { useState } from "react";
import { Activity, ArrowRight, Check, Clock3, Download, MapPin, Menu, Package, Plus, Route, ShieldCheck, TrainFront, Trash2, Truck, UserRound, Wallet, X } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const newShipment = () => ({
  id: crypto.randomUUID(), origin: "", destination: "", cargo_type: "General goods",
  weight_tonnes: "10", priority: "balanced", wagon_preference: "No preference"
});
const money = (n) => new Intl.NumberFormat("en-IN", {
  style: "currency", currency: "INR", maximumFractionDigits: 0
}).format(n ?? 0);

export default function App() {
  const [shipments, setShipments] = useState([newShipment()]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState([]);
  const [view, setView] = useState("planner");
  const [menuOpen, setMenuOpen] = useState(false);

  // Update only the field changed by the user in the selected shipment.
  const update = (id, key, value) => setShipments(list =>
    list.map(item => item.id === id ? { ...item, [key]: value } : item)
  );
  const addShipment = () => setShipments(list => [...list, newShipment()]);
  const removeShipment = id => setShipments(list =>
    list.length > 1 ? list.filter(item => item.id !== id) : list
  );

  // Ask the backend to plan each shipment independently; Promise.all keeps the UI simple.
  async function generatePlans(event) {
    event.preventDefault();
    setLoading(true); setError(""); setResults([]); setConfirmed([]);
    try {
      const plans = await Promise.all(shipments.map(async shipment => {
        const response = await fetch(`${API_BASE}/api/plan`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            origin: shipment.origin.trim(), destination: shipment.destination.trim(),
            cargo_type: shipment.cargo_type, weight_tonnes: Number(shipment.weight_tonnes),
            priority: shipment.priority, wagon_preference: shipment.wagon_preference
          })
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
        return { shipmentId: shipment.id, ...body };
      }));
      setResults(plans);
    } catch (err) {
      setError(`${err.message}. Check that the backend is running at ${API_BASE}.`);
    } finally { setLoading(false); }
  }

  // This saves a prototype confirmation only. It is not a real railway booking.
  async function confirmPlan(result) {
    const shipment = shipments.find(item => item.id === result.shipmentId);
    try {
      const response = await fetch(`${API_BASE}/api/bookings/confirm`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ shipment, selected_option: result.options[0] })
      });
      if (!response.ok) throw new Error("Confirmation could not be saved");
      setConfirmed(list => [...list, result.shipmentId]);
    } catch (err) { setError(err.message); }
  }

  // Export all visible options to a spreadsheet-friendly CSV file.
  function exportCSV() {
    const rows = [["Shipment", "Origin", "Destination", "Rank", "Route", "Wagon", "Estimated INR", "Transit hours", "Priority"]];
    results.forEach((result, index) => {
      const shipment = shipments.find(item => item.id === result.shipmentId);
      result.options.forEach(option => rows.push([
        index + 1, shipment?.origin, shipment?.destination, option.rank, option.route_name,
        option.wagon_type, option.estimated_cost_inr, option.estimated_transit_hours, shipment?.priority
      ]));
    });
    const csv = rows.map(row => row.map(value =>
      `"${String(value ?? "").replaceAll('"', '""')}"`
    ).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url; link.download = "rail-optimizer-options.csv"; link.click();
    URL.revokeObjectURL(url);
  }

  return <div className="app-shell">
    <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
      <a className="brand" href="#" onClick={() => setView("planner")}>
        <div className="brand-mark"><TrainFront size={25}/></div>
        <div><strong>RAIL<span>OPT</span></strong><small>OPTIMIZER AI</small></div>
        <button className="mobile-close" onClick={e => { e.preventDefault(); setMenuOpen(false); }} aria-label="Close menu"><X size={18}/></button>
      </a>
      <div className="workspace-label">WORKSPACE</div>
      <button className={`nav-item ${view === "planner" ? "active" : ""}`} onClick={() => setView("planner")}><Route size={18}/> Freight planner</button>
      <button className={`nav-item ${view === "bookings" ? "active" : ""}`} onClick={() => setView("bookings")}><Package size={18}/> My bookings <span className="nav-count">{confirmed.length}</span></button>
      <button className={`nav-item ${view === "network" ? "active" : ""}`} onClick={() => setView("network")}><Activity size={18}/> Network overview</button>
      <div className="sidebar-bottom">
        <div className="help-card"><ShieldCheck size={18}/><strong>Plan with clarity</strong><p>Compare options before choosing a freight plan.</p></div>
        <div className="profile-row"><div className="avatar"><UserRound size={17}/></div><div><strong>Guest workspace</strong><small>Prototype mode</small></div></div>
      </div>
    </aside>

    <main className="main-area">
      <header className="topbar">
        <button className="menu-toggle" onClick={() => setMenuOpen(true)} aria-label="Open menu"><Menu size={21}/></button>
        <div className="breadcrumb">Workspace <span>/</span> <strong>{view === "planner" ? "Freight planner" : view === "bookings" ? "My bookings" : "Network overview"}</strong></div>
        <div className="topbar-right"><span className="status-dot"/> Prototype online <div className="top-avatar">G</div></div>
      </header>

      {view === "planner" && <div className="page-content">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><span/> SMARTER FREIGHT. CLEARER DECISIONS.</div>
            <h1>Move goods<br/>with <em>confidence.</em></h1>
            <p>Plan railway freight with route alternatives, transparent cost estimates, and wagon suggestions — all in one place.</p>
            <div className="hero-tags"><span><Route size={15}/> Multi-route planning</span><span><Wallet size={15}/> Cost comparison</span><span><TrainFront size={15}/> Wagon matching</span></div>
          </div>
          <div className="hero-art" aria-label="Decorative route illustration">
            <div className="art-grid"/><div className="route-line line-one"/><div className="route-line line-two"/>
            <div className="route-node node-a"><MapPin size={18}/></div><div className="route-node node-b"><MapPin size={18}/></div><div className="route-node node-c"><MapPin size={18}/></div>
            <div className="art-label label-a">● ORIGIN</div><div className="art-label label-b">● ALTERNATE ROUTE</div>
            <div className="art-train"><TrainFront size={38}/></div><div className="art-caption"><span>ROUTE INTELLIGENCE</span><strong>Plan beyond the obvious.</strong></div>
          </div>
        </section>

        <section className="planner-section">
          <div className="section-heading"><div><div className="eyebrow">START A NEW PLAN</div><h2>Shipment details</h2><p>Enter each shipment below. Add more when planning multiple orders.</p></div><div className="secure-label"><ShieldCheck size={16}/> Prototype workspace</div></div>
          <form onSubmit={generatePlans}>
            {shipments.map((shipment, index) => <article className="shipment-card" key={shipment.id}>
              <div className="shipment-card-head"><div className="shipment-number">{String(index + 1).padStart(2, "0")}</div><div><h3>Shipment {index + 1}</h3><p>Route, cargo and delivery priorities</p></div>
                {shipments.length > 1 && <button type="button" className="icon-button delete-button" onClick={() => removeShipment(shipment.id)} aria-label="Remove shipment"><Trash2 size={17}/></button>}
              </div>
              <div className="form-grid">
                <label className="field"><span>Origin station / city</span><div className="input-wrap"><MapPin size={17}/><input required value={shipment.origin} onChange={e => update(shipment.id, "origin", e.target.value)} placeholder="e.g. Delhi"/></div></label>
                <div className="swap-holder">→</div>
                <label className="field"><span>Destination station / city</span><div className="input-wrap"><MapPin size={17}/><input required value={shipment.destination} onChange={e => update(shipment.id, "destination", e.target.value)} placeholder="e.g. Mumbai"/></div></label>
                <label className="field"><span>Cargo type</span><div className="input-wrap"><Package size={17}/><select value={shipment.cargo_type} onChange={e => update(shipment.id, "cargo_type", e.target.value)}>{["General goods","Food grains","Cement","Coal","Steel","Fertilizer","Containers","Automobiles","Other"].map(v => <option key={v}>{v}</option>)}</select></div></label>
                <label className="field"><span>Shipment weight (tonnes)</span><div className="input-wrap"><Truck size={17}/><input type="number" min="0.1" step="0.1" required value={shipment.weight_tonnes} onChange={e => update(shipment.id, "weight_tonnes", e.target.value)}/></div></label>
                <label className="field"><span>Wagon preference</span><div className="input-wrap"><TrainFront size={17}/><select value={shipment.wagon_preference} onChange={e => update(shipment.id, "wagon_preference", e.target.value)}>{["No preference","BOXN","BCN","BCNA","Container flat","Covered wagon","Open wagon"].map(v => <option key={v}>{v}</option>)}</select></div></label>
                <label className="field"><span>Optimization priority</span><div className="input-wrap"><Activity size={17}/><select value={shipment.priority} onChange={e => update(shipment.id, "priority", e.target.value)}><option value="balanced">Balanced plan</option><option value="cost">Lowest estimated cost</option><option value="time">Shortest estimated time</option><option value="reliability">Reliability first</option></select></div></label>
              </div>
            </article>)}
            <div className="form-actions"><button type="button" className="button-secondary" onClick={addShipment}><Plus size={17}/> Add shipment</button><button type="submit" className="button-primary" disabled={loading}>{loading ? "Planning routes..." : <>Generate route options <ArrowRight size={17}/></>}</button></div>
          </form>
          {error && <div className="error-banner">{error}</div>}
          {results.length > 0 && <section className="results-section">
            <div className="results-heading"><div><div className="eyebrow">PLANNING RESULTS</div><h2>Your route options</h2><p>Illustrative estimates — verify against official rates and current operations.</p></div><button className="button-secondary" onClick={exportCSV}><Download size={16}/> Export CSV</button></div>
            {results.map((result, index) => {
              const shipment = shipments.find(item => item.id === result.shipmentId);
              return <article className="result-card" key={result.shipmentId}>
                <div className="result-card-head"><div><span className="result-label">SHIPMENT {index + 1}</span><h3>{shipment?.origin} <ArrowRight size={16}/> {shipment?.destination}</h3></div>{confirmed.includes(result.shipmentId) ? <span className="confirmed-pill"><Check size={14}/> Confirmed in prototype</span> : <span className="estimate-pill">Estimate only</span>}</div>
                <div className="route-options">{result.options.map(option => <div className={`route-option ${option.rank === 1 ? "recommended" : ""}`} key={option.rank}>
                  <div className="option-top"><span className="option-rank">{option.rank === 1 ? "BEST MATCH" : `OPTION ${option.rank}`}</span><span className="priority-chip">{option.priority_label}</span></div>
                  <h4>{option.route_name}</h4><p className="route-description">{option.route_description}</p>
                  <div className="option-metrics"><div><Wallet size={16}/><small>Est. cost</small><strong>{money(option.estimated_cost_inr)}</strong></div><div><Clock3 size={16}/><small>Transit estimate</small><strong>{option.estimated_transit_hours} hrs</strong></div><div><TrainFront size={16}/><small>Wagon suggestion</small><strong>{option.wagon_type}</strong></div></div>
                  <p className="why-line"><ShieldCheck size={15}/>{option.explanation}</p>
                </div>)}</div>
                {!confirmed.includes(result.shipmentId) && <button className="button-primary confirm-button" onClick={() => confirmPlan(result)}>Confirm preferred plan <Check size={16}/></button>}
              </article>;
            })}
          </section>}
        </section>
        <footer className="footer-note">Rail Optimizer AI <span>•</span> Planning support, not a confirmed railway booking.</footer>
      </div>}

      {view === "bookings" && <div className="simple-page"><div className="eyebrow">WORKSPACE</div><h1>My bookings</h1><p className="simple-intro">Confirmed plans from this current session.</p>
        {confirmed.length === 0 ? <div className="empty-state"><Package size={30}/><h3>No confirmed plans yet</h3><p>Generate route options and confirm a plan to see it here.</p><button className="button-primary" onClick={() => setView("planner")}>Plan a shipment <ArrowRight size={16}/></button></div> :
          confirmed.map(id => { const s = shipments.find(item => item.id === id); return <div className="booking-row" key={id}><div className="booking-icon"><Check size={18}/></div><div><strong>{s?.origin} → {s?.destination}</strong><p>{s?.cargo_type} · {s?.weight_tonnes} tonnes</p></div><span className="confirmed-pill">Prototype confirmation</span></div>; })}
      </div>}

      {view === "network" && <div className="simple-page"><div className="eyebrow">NETWORK OVERVIEW</div><h1>Route network</h1><p className="simple-intro">A visual placeholder for future route and traffic layers.</p>
        <div className="network-placeholder"><div className="network-grid"/><div className="network-path path-one"/><div className="network-path path-two"/><div className="network-path path-three"/><span className="network-pin pin-one">DEL</span><span className="network-pin pin-two">BOM</span><span className="network-pin pin-three">KOL</span><div className="network-legend"><span><i className="green-line"/> Lower illustrative load</span><span><i className="yellow-line"/> Moderate illustrative load</span><span><i className="red-line"/> Higher illustrative load</span></div></div>
        <p className="map-disclaimer">This is not live railway traffic data. Verified station coordinates and operational feeds are needed for a real map.</p>
      </div>}
    </main>
  </div>;
}
