import { useEffect, useState } from "react";
import { Link, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { Activity, Boxes, ChevronRight, CircleDot, Clock3, FlaskConical, GitBranch, LayoutDashboard, Plus, RefreshCw, ShieldCheck, TriangleAlert } from "lucide-react";
import { api, type EventRecord, type Experiment, type GraphData, type GraphEdge, type Investigation } from "./api";

const navItems = [
  ["/", "Dashboard", LayoutDashboard],
  ["/graph", "Attack graph", GitBranch],
  ["/timeline", "Event timeline", Clock3],
  ["/evidence", "Evidence inspector", ShieldCheck],
  ["/experiments", "Research & experiments", FlaskConical],
] as const;

function App() {
  const location = useLocation();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedId, setSelectedId] = useState<string>();
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [selectedNode, setSelectedNode] = useState<EventRecord | null>(null);
  const [error, setError] = useState("");
  const [backend, setBackend] = useState("checking");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newInvestigationName, setNewInvestigationName] = useState("");
  const navigate = useNavigate();

  const refresh = async () => {
    try {
      setError("");
      const [items, health] = await Promise.all([api.investigations(), api.health()]);
      setInvestigations(items);
      setBackend(health.persistence);
      const id = selectedId ?? items[0]?.id;
      if (id) {
        setSelectedId(id);
        const [nextEvents, nextGraph] = await Promise.all([api.events(id), api.graph(id)]);
        setEvents(nextEvents);
        setGraph(nextGraph);
      }
    } catch (caught) {
      setBackend("unavailable");
      setError(caught instanceof Error ? caught.message : "Backend unavailable");
    }
  };

  useEffect(() => { void refresh(); }, [selectedId]);

  const createInvestigation = async () => {
    const name = newInvestigationName.trim();
    if (!name) return;
    try {
      const created = await api.createInvestigation(name);
      setInvestigations((current) => [...current, created]);
      setSelectedId(created.id);
      setNewInvestigationName("");
      setShowCreateForm(false);
      navigate("/");
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Could not create investigation"); }
  };

  const reconstruct = async () => {
    if (!selectedId) return;
    try { setGraph(await api.reconstruct(selectedId)); } catch (caught) { setError(caught instanceof Error ? caught.message : "Reconstruction failed"); }
  };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Activity size={18} /></div><div><strong>ECHO</strong><span>FORENSICS LAB</span></div></div>
      <div className="side-label">WORKSPACE</div>
      <select className="investigation-select" value={selectedId ?? ""} onChange={(event) => setSelectedId(event.target.value)}>
        <option value="">No investigation selected</option>
        {investigations.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
      </select>
      <nav>{navItems.map(([path, label, Icon]) => <Link key={path} to={path} className={location.pathname === path ? "nav-link active" : "nav-link"}><Icon size={17} /><span>{label}</span><ChevronRight size={14} className="nav-arrow" /></Link>)}</nav>
      <button className="new-investigation" onClick={() => void createInvestigation()}><Plus size={16} /> New investigation</button>
      <div className="sidebar-footer"><div className="status-dot" /> Local research mode<div className="version">ECHO 0.1.0.dev0</div></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><span className="eyebrow">CURRENT INVESTIGATION</span><strong>{investigations.find((item) => item.id === selectedId)?.name ?? "No active investigation"}</strong></div><div className="topbar-context"><span className={backend === "unavailable" ? "health bad" : "health"}><CircleDot size={12} /> {backend === "memory-development-fallback" ? "LOCAL FALLBACK" : backend.toUpperCase()}</span><button className="icon-button" title="Refresh data" onClick={() => void refresh()}><RefreshCw size={16} /></button></div></header>
      {error && <div className="alert"><TriangleAlert size={16} /> <span>{error}</span></div>}
      {showCreateForm && <form className="create-form" onSubmit={(event) => { event.preventDefault(); void createInvestigation(); }}><label htmlFor="investigation-name">Investigation name</label><input id="investigation-name" autoFocus maxLength={200} value={newInvestigationName} onChange={(event) => setNewInvestigationName(event.target.value)} placeholder="e.g. Synthetic chain review" /><div className="button-row"><button className="primary-button" type="submit" disabled={!newInvestigationName.trim()}>Create</button><button className="secondary-button" type="button" onClick={() => setShowCreateForm(false)}>Cancel</button></div></form>}
      <div className="page-wrap"><Routes>
        <Route path="/" element={<Dashboard investigationId={selectedId} investigations={investigations} events={events} graph={graph} onCreate={() => setShowCreateForm(true)} onGenerate={async () => { if (!selectedId) return; try { const scenario = await api.syntheticScenario(17); await api.importEvents(selectedId, scenario.events); await refresh(); } catch (caught) { setError(caught instanceof Error ? caught.message : "Synthetic import failed"); } }} onReconstruct={() => void reconstruct()} onOpenGraph={() => navigate("/graph")} />} />
        <Route path="/graph" element={<GraphScreen graph={graph} selectedEdge={selectedEdge} selectedNode={selectedNode} onSelectEdge={setSelectedEdge} onSelectNode={setSelectedNode} />} />
        <Route path="/timeline" element={<TimelineScreen events={events} />} />
        <Route path="/evidence" element={<EvidenceScreen edge={selectedEdge ?? graph?.edges[0] ?? null} />} />
        <Route path="/experiments" element={<ExperimentsScreen />} />
      </Routes></div>
    </main>
  </div>;
}

function Dashboard({ investigationId, investigations, events, graph, onCreate, onGenerate, onReconstruct, onOpenGraph }: { investigationId?: string; investigations: Investigation[]; events: EventRecord[]; graph: GraphData | null; onCreate: () => void; onGenerate: () => Promise<void>; onReconstruct: () => void; onOpenGraph: () => void }) {
  return <section><PageHeading kicker="INVESTIGATION DASHBOARD" title="Signal, context, chain." action={<button className="primary-button" onClick={onCreate}><Plus size={16} /> New investigation</button>} />
    {investigations.length === 0 ? <EmptyState title="No investigations yet" text="Create a local investigation to begin importing synthetic evidence." action={<button className="primary-button" onClick={onCreate}><Plus size={16} /> Create investigation</button>} /> : <>
      <div className="metric-grid"><Metric label="Observed events" value={events.length} /><Metric label="Proposed relationships" value={graph?.edges.length ?? 0} /><Metric label="Rejected candidates" value={graph?.rejected_candidates.length ?? 0} /><Metric label="Graph status" value={graph?.version ? `v${graph.version}` : "Not run"} /></div>
      <div className="split-grid"><Panel title="Reconstruction status" meta="CURRENT RUN"><div className="run-status"><div className="status-icon"><GitBranch size={20} /></div><div><strong>{graph?.version ? "Graph available" : "Awaiting reconstruction"}</strong><p>{graph?.version ? "Evidence-backed hypotheses are ready for review." : "Import events, then run the core reconstruction engine."}</p></div></div><div className="button-row"><button className="primary-button" disabled={!investigationId} onClick={() => void onGenerate()}><Boxes size={15} /> Generate synthetic evidence</button><button className="primary-button" disabled={!events.length} onClick={onReconstruct}><GitBranch size={15} /> Run reconstruction</button><button className="secondary-button" onClick={onOpenGraph}>Open graph <ChevronRight size={15} /></button></div></Panel><Panel title="Workspace scope" meta="RESEARCH BOUNDARY"><div className="scope-list"><span><CircleDot size={13} /> Synthetic evidence only</span><span><CircleDot size={13} /> Ground truth isolated</span><span><CircleDot size={13} /> Correlation is not causation</span></div></Panel></div>
    </>}
  </section>;
}

function GraphScreen({ graph, selectedEdge, selectedNode, onSelectEdge, onSelectNode }: { graph: GraphData | null; selectedEdge: GraphEdge | null; selectedNode: EventRecord | null; onSelectEdge: (edge: GraphEdge) => void; onSelectNode: (node: EventRecord) => void }) {
  return <section><PageHeading kicker="ATTACK GRAPH EXPLORER" title="Observed events, proposed links." action={<span className="read-only-label"><CircleDot size={12} /> Evidence view</span>} />{!graph?.nodes.length ? <EmptyState title="Graph not available" text="Select an investigation with events and run reconstruction first." /> : <div className="graph-layout"><Panel title="Relationship map" meta={`${graph.nodes.length} NODES / ${graph.edges.length} EDGES`}><div className="graph-canvas">{graph.nodes.map((node, index) => <button className={`graph-node ${selectedNode?.event_id === node.event_id ? "selected" : ""}`} style={{ left: `${10 + (index % 3) * 30}%`, top: `${12 + Math.floor(index / 3) * 28}%` }} key={node.event_id} onClick={() => onSelectNode(node)}><span className="node-type">{node.event_type}</span><strong>{node.event_id}</strong><small>{new Date(node.event_time).toLocaleTimeString()}</small></button>)}</div><div className="graph-legend"><span><i className="legend-node" /> Observed event</span><span><i className="legend-edge" /> Proposed relationship</span><span><i className="legend-muted" /> Disconnected / unlinked</span></div></Panel><div>{selectedNode && <Panel title="Selected event" meta="OBSERVED"><div className="relationship-hero"><code>{selectedNode.event_id}</code><span>{selectedNode.event_type}</span></div><p className="muted-copy">Event time: {new Date(selectedNode.event_time).toLocaleString()}<br />Observed time: {new Date(selectedNode.observed_time).toLocaleString()}<br />Host: {selectedNode.host_id ?? "unknown"} · User: {selectedNode.user_id ?? "unknown"}</p></Panel>}<EvidenceCard edge={selectedEdge ?? graph.edges[0] ?? null} onSelect={onSelectEdge} /></div></div>}</section>;
}

function TimelineScreen({ events }: { events: EventRecord[] }) { const [selected, setSelected] = useState<EventRecord | null>(null); return <section><PageHeading kicker="EVENT TIMELINE" title="When it happened. When it arrived." action={<span className="read-only-label"><Clock3 size={13} /> Event-time semantics</span>} />{!events.length ? <EmptyState title="No event records" text="Imported evidence will appear here with event time and observed time kept distinct." /> : <><Panel title="Observed evidence" meta={`${events.length} RECORDS`}><div className="timeline">{events.map((event) => <button className="timeline-row" key={event.event_id} onClick={() => setSelected(event)}><div className="timeline-marker" /><div className="timeline-main"><div className="event-title"><strong>{event.event_type}</strong><code>{event.event_id}</code></div><p>{event.host_id ?? "unknown host"} · {event.user_id ?? "unknown identity"}</p></div><div className="time-cell"><span>EVENT</span>{new Date(event.event_time).toLocaleString()}</div><div className="time-cell observed"><span>OBSERVED</span>{new Date(event.observed_time).toLocaleString()}</div></button>)}</div></Panel>{selected && <Panel title="Selected event" meta="TIMELINE DETAIL"><div className="relationship-hero"><code>{selected.event_id}</code><span>{selected.event_type}</span></div><p className="muted-copy">Event time: {new Date(selected.event_time).toLocaleString()}<br />Observed time: {new Date(selected.observed_time).toLocaleString()}<br />Source: {selected.source ?? "unknown"}</p></Panel>}</>}</section>; }

function EvidenceScreen({ edge }: { edge: GraphEdge | null }) { return <section><PageHeading kicker="EVIDENCE INSPECTOR" title="Why this link exists." />{!edge ? <EmptyState title="Select a relationship" text="Choose an edge in the graph view to inspect its evidence, contradictions, and alternatives." /> : <div className="evidence-layout"><Panel title="Relationship" meta={edge.evidence_strength.toUpperCase()}><div className="relationship-hero"><code>{edge.source_event_id}</code><ChevronRight size={17} /><code>{edge.target_event_id}</code></div><div className="relationship-type">{edge.relationship_type.replaceAll("_", " ")}</div><p className="explanation">{edge.explanation}</p><div className="score-line"><span>Rule-based score</span><strong>{edge.score}</strong></div></Panel><div className="evidence-columns"><EvidenceList title="Supporting evidence" items={edge.supporting_evidence} tone="good" /><EvidenceList title="Contradictory evidence" items={edge.contradictory_evidence} tone="bad" /><EvidenceList title="Missing evidence" items={edge.missing_evidence} tone="muted" /></div><Panel title="Alternative interpretations"><ul className="plain-list">{edge.alternative_interpretations.map((item) => <li key={item}>{item}</li>)}</ul></Panel></div>}</section>; }

function ExperimentsScreen() { const [runs, setRuns] = useState<Experiment[]>([]); const [loading, setLoading] = useState(false); const [message, setMessage] = useState(""); const run = async () => { setLoading(true); try { const result = await api.runExperiment(Math.floor(Math.random() * 1000)); setRuns((current) => [result, ...current]); setMessage("Experiment completed with measured metrics."); } catch (caught) { setMessage(caught instanceof Error ? caught.message : "Experiment failed"); } finally { setLoading(false); } }; useEffect(() => { void api.experiments().then(setRuns).catch(() => setMessage("Research API unavailable")); }, []); return <section><PageHeading kicker="RESEARCH & EXPERIMENTS" title="Measure the reconstruction." action={<button className="primary-button" onClick={() => void run()} disabled={loading}><FlaskConical size={16} /> {loading ? "Running..." : "Run experiment"}</button>} />{message && <div className="inline-message">{message}</div>}{!runs.length ? <EmptyState title="No experiment runs" text="Run a controlled synthetic experiment to see actual metrics here." /> : <div className="experiment-list">{runs.map((run) => <Panel key={run.id} title={run.id} meta={run.status.toUpperCase()}><div className="experiment-meta"><span>Scenario <strong>{run.scenario_id}</strong></span><span>Seed <strong>{run.seed}</strong></span></div><div className="metric-grid compact">{["edge_precision", "edge_recall", "edge_f1", "false_link_rate", "reconstruction_coverage"].map((key) => <Metric key={key} label={key.replaceAll("_", " ")} value={typeof run.metrics[key] === "number" ? Number(run.metrics[key]).toFixed(3) : "-"} />)}</div></Panel>)}</div>}</section>; }

function PageHeading({ kicker, title, action }: { kicker: string; title: string; action?: React.ReactNode }) { return <div className="page-heading"><div><span className="eyebrow">{kicker}</span><h1>{title}</h1></div>{action}</div>; }
function Panel({ title, meta, children }: { title: string; meta?: string; children: React.ReactNode }) { return <div className="panel"><div className="panel-heading"><h2>{title}</h2>{meta && <span>{meta}</span>}</div>{children}</div>; }
function Metric({ label, value }: { label: string; value: React.ReactNode }) { return <div className="metric"><span>{label}</span><strong>{value}</strong></div>; }
function EmptyState({ title, text, action }: { title: string; text: string; action?: React.ReactNode }) { return <div className="empty-state"><Boxes size={28} /><h2>{title}</h2><p>{text}</p>{action}</div>; }
function EvidenceCard({ edge, onSelect }: { edge: GraphEdge | null; onSelect: (edge: GraphEdge) => void }) { return <Panel title="Evidence queue" meta={edge ? "SELECTED" : "EMPTY"}>{edge ? <button className="evidence-row" onClick={() => onSelect(edge)}><span className="strength-dot" /><div><strong>{edge.relationship_type.replaceAll("_", " ")}</strong><small>{edge.source_event_id} → {edge.target_event_id}</small></div><span className="score">{edge.score}</span></button> : <p className="muted-copy">No proposed relationships are available.</p>}</Panel>; }
function EvidenceList({ title, items, tone }: { title: string; items: string[]; tone: string }) { return <Panel title={title}><ul className={`evidence-list ${tone}`}>{items.length ? items.map((item) => <li key={item}>{item}</li>) : <li>No evidence recorded.</li>}</ul></Panel>; }

export default App;
