import { useEffect, useMemo, useState } from 'react'

type Document = {
  id: string; type: string; title: string; description?: string | null; tags: string[]
  resource?: string | null; timestamp?: string | null; body: string; links: string[]
}
type Graph = { nodes: { id: string; label: string; type: string; tags: string[] }[]; edges: { source: string; target: string }[] }

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function GraphView({ graph, activeId, select }: { graph: Graph; activeId: string | null; select: (id: string) => void }) {
  const count = Math.max(graph.nodes.length, 1)
  const points = Object.fromEntries(graph.nodes.map((node, index) => {
    const angle = (Math.PI * 2 * index) / count - Math.PI / 2
    return [node.id, { x: 50 + Math.cos(angle) * 36, y: 50 + Math.sin(angle) * 34 }]
  }))
  return <div className="graph-wrap"><svg className="graph" viewBox="0 0 100 100" role="img" aria-label="Knowledge graph">
    {graph.edges.map((edge) => <line key={`${edge.source}-${edge.target}`} x1={points[edge.source]?.x} y1={points[edge.source]?.y} x2={points[edge.target]?.x} y2={points[edge.target]?.y} className="edge" />)}
    {graph.nodes.map((node) => <g key={node.id} onClick={() => select(node.id)} className="node-group"><circle cx={points[node.id].x} cy={points[node.id].y} r="7" className={activeId === node.id ? 'node active' : 'node'} /><text x={points[node.id].x} y={points[node.id].y + 1} className="node-label">{node.label.slice(0, 7)}</text></g>)}
  </svg></div>
}

export default function App() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [graph, setGraph] = useState<Graph>({ nodes: [], edges: [] })
  const [activeId, setActiveId] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [showIngest, setShowIngest] = useState(false)
  const [form, setForm] = useState({ type: 'Concept', title: '', description: '', tags: '', resource: '', body: '# Overview\n\n' })
  useEffect(() => {
    Promise.all([fetch(`${API}/documents`), fetch(`${API}/graph`)]).then(async ([docs, graphResponse]) => {
      if (!docs.ok || !graphResponse.ok) throw new Error('API connection failed')
      const loaded = await docs.json() as Document[]
      setDocuments(loaded); setGraph(await graphResponse.json()); setActiveId(loaded[0]?.id ?? null)
    }).catch(() => setError('API에 연결하지 못했습니다. Docker Compose 스택이 실행 중인지 확인하세요.'))
  }, [])
  async function submitIngest(event: React.FormEvent) {
    event.preventDefault()
    const response = await fetch(`${API}/documents`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, tags: form.tags.split(',').map(tag => tag.trim()).filter(Boolean) }) })
    if (!response.ok) { setError('문서 저장에 실패했습니다. 같은 제목의 문서가 있는지 확인하세요.'); return }
    setShowIngest(false)
    window.location.reload()
  }
  const filtered = useMemo(() => documents.filter((doc) => `${doc.title} ${doc.description ?? ''} ${doc.tags.join(' ')}`.toLowerCase().includes(query.toLowerCase())), [documents, query])
  const active = documents.find((doc) => doc.id === activeId) ?? filtered[0]
  return <main className="app-shell">
    <aside className="sidebar"><div className="brand"><span className="brand-mark">K</span><span>Knowledge<br/><b>Wiki</b></span></div><nav><button className="nav-item active">▦ Workspace</button><button className="nav-item">⌘ Concepts</button><button className="nav-item">◌ Sources</button><button className="nav-item">⌁ Activity</button></nav><div className="sidebar-footer"><span className="status-dot"/> OKF v0.1<br/><small>Markdown is the source of truth</small></div></aside>
    <section className="workspace"><header><div><p className="eyebrow">LOCAL KNOWLEDGE SYSTEM</p><h1>Knowledge Workspace</h1></div><div className="header-actions"><button className="quiet-button">↻ Sync index</button><button className="primary-button" onClick={() => setShowIngest(true)}>＋ Ingest document</button></div></header>
      <div className="metric-row"><div className="metric"><span>Concepts</span><strong>{documents.length}</strong></div><div className="metric"><span>Relationships</span><strong>{graph.edges.length}</strong></div><div className="metric"><span>Format</span><strong>OKF</strong></div><div className="metric"><span>Search index</span><strong>Ready</strong></div></div>
      {error && <div className="error">{error}</div>}
      <div className="content-grid"><section className="panel graph-panel"><div className="panel-title"><div><p className="eyebrow">RELATIONSHIP MAP</p><h2>Knowledge Graph</h2></div><span className="pill">{graph.nodes.length} nodes</span></div><GraphView graph={graph} activeId={active?.id ?? null} select={setActiveId}/><p className="hint">Click a concept to inspect its OKF document and links.</p></section>
      <section className="panel document-panel">{active ? <><div className="document-type">{active.type}</div><h2>{active.title}</h2><p className="description">{active.description}</p><div className="tags">{active.tags.map(tag => <span key={tag}>#{tag}</span>)}</div><pre>{active.body}</pre><div className="document-footer"><code>{active.id}.md</code>{active.resource && <a href={active.resource} target="_blank">Source ↗</a>}</div></> : <div className="empty">아직 문서가 없습니다. 첫 OKF 문서를 적재하세요.</div>}</section></div>
      <section className="panel list-panel"><div className="panel-title"><div><p className="eyebrow">BROWSE</p><h2>Concept Library</h2></div><input aria-label="Search concepts" placeholder="Search titles, descriptions, tags…" value={query} onChange={event => setQuery(event.target.value)} /></div><div className="concept-list">{filtered.map(doc => <button className={doc.id === active?.id ? 'concept-card selected' : 'concept-card'} key={doc.id} onClick={() => setActiveId(doc.id)}><span className="card-type">{doc.type}</span><strong>{doc.title}</strong><p>{doc.description}</p><span className="card-path">{doc.id}.md</span></button>)}</div></section>
      {showIngest && <div className="modal-backdrop"><form className="ingest-form" onSubmit={submitIngest}><div className="panel-title"><div><p className="eyebrow">CREATE OKF CONCEPT</p><h2>Ingest document</h2></div><button type="button" className="close-button" onClick={() => setShowIngest(false)}>×</button></div><label>Document title<input aria-label="Document title" required value={form.title} onChange={event => setForm({ ...form, title: event.target.value })}/></label><label>Type<input value={form.type} onChange={event => setForm({ ...form, type: event.target.value })}/></label><label>Description<input value={form.description} onChange={event => setForm({ ...form, description: event.target.value })}/></label><label>Tags <small>(comma-separated)</small><input value={form.tags} onChange={event => setForm({ ...form, tags: event.target.value })}/></label><label>Resource URL<input type="url" value={form.resource} onChange={event => setForm({ ...form, resource: event.target.value })}/></label><label>Markdown body<textarea aria-label="Markdown body" required value={form.body} onChange={event => setForm({ ...form, body: event.target.value })}/></label><button className="primary-button" type="submit">Save OKF document</button></form></div>}
    </section>
  </main>
}
