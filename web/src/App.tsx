import { useEffect, useMemo, useState, type ReactNode } from 'react'

type Document = {
  id: string; type: string; title: string; description?: string | null; tags: string[]
  resource?: string | null; timestamp?: string | null; body: string; links: string[]
  title_ko?: string | null; description_ko?: string | null; body_ko?: string | null
}
type Graph = { nodes: { id: string; label: string; type: string; tags: string[] }[]; edges: { source: string; target: string }[] }

const configuredApi = import.meta.env.VITE_API_URL
const isLocalBrowser = ['localhost', '127.0.0.1'].includes(window.location.hostname)
const API = configuredApi && isLocalBrowser ? configuredApi : `${window.location.protocol}//${window.location.hostname}:8000/api`
const groupLabels: Record<string, string> = { Concept: '개념', Comparison: '비교', Project: '프로젝트', Source: '출처' }
const groupOrder = ['Concept', 'Comparison', 'Project', 'Source']
const typeLabel = (type: string) => groupLabels[type] ?? type

function GraphView({ graph, activeId, select }: { graph: Graph; activeId: string | null; select: (id: string) => void }) {
  const count = Math.max(graph.nodes.length, 1)
  const points = Object.fromEntries(graph.nodes.map((node, index) => {
    const angle = (Math.PI * 2 * index) / count - Math.PI / 2
    return [node.id, { x: 50 + Math.cos(angle) * 36, y: 50 + Math.sin(angle) * 34 }]
  }))
  return <div className="graph-wrap"><svg className="graph" viewBox="0 0 100 100" role="img" aria-label="지식 그래프">
    {graph.edges.map((edge) => <line key={`${edge.source}-${edge.target}`} x1={points[edge.source]?.x} y1={points[edge.source]?.y} x2={points[edge.target]?.x} y2={points[edge.target]?.y} className="edge" />)}
    {graph.nodes.map((node) => <g key={node.id} onClick={() => select(node.id)} className="node-group"><circle cx={points[node.id].x} cy={points[node.id].y} r="7" className={activeId === node.id ? 'node active' : 'node'} /><text x={points[node.id].x} y={points[node.id].y + 1} className="node-label">{node.label.slice(0, 7)}</text></g>)}
  </svg></div>
}

function MarkdownView({ body }: { body: string }) {
  const lines = body.replace(/\r/g, '').split('\n')
  const blocks: ReactNode[] = []
  for (let index = 0; index < lines.length;) {
    const line = lines[index]
    if (!line.trim()) { index += 1; continue }
    if (line.startsWith('```')) {
      const code: string[] = []
      index += 1
      while (index < lines.length && !lines[index].startsWith('```')) code.push(lines[index++])
      if (index < lines.length) index += 1
      blocks.push(<pre className="markdown-code" key={`code-${index}`}><code>{code.join('\n')}</code></pre>)
      continue
    }
    const heading = line.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      const level = heading[1].length
      blocks.push(level === 1 ? <h2 key={`heading-${index}`}>{heading[2]}</h2> : level === 2 ? <h3 key={`heading-${index}`}>{heading[2]}</h3> : <h4 key={`heading-${index}`}>{heading[2]}</h4>)
      index += 1
      continue
    }
    if (/^\|.*\|\s*$/.test(line)) {
      const rows: string[][] = []
      while (index < lines.length && /^\|.*\|\s*$/.test(lines[index])) {
        const cells = lines[index].trim().slice(1, -1).split('|').map(cell => cell.trim())
        if (!cells.every(cell => /^:?-{3,}:?$/.test(cell))) rows.push(cells)
        index += 1
      }
      if (rows.length) blocks.push(<div className="table-scroll" key={`table-${index}`}><table><thead><tr>{rows[0].map((cell, cellIndex) => <th key={cellIndex}>{cell}</th>)}</tr></thead><tbody>{rows.slice(1).map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}</tr>)}</tbody></table></div>)
      continue
    }
    if (/^[-*]\s+/.test(line)) {
      const items: string[] = []
      while (index < lines.length && /^[-*]\s+/.test(lines[index])) items.push(lines[index++].replace(/^[-*]\s+/, ''))
      blocks.push(<ul key={`list-${index}`}>{items.map((item, itemIndex) => <li key={itemIndex}>{item}</li>)}</ul>)
      continue
    }
    blocks.push(<p key={`paragraph-${index}`}>{line}</p>)
    index += 1
  }
  return <>{blocks}</>
}

export default function App() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [graph, setGraph] = useState<Graph>({ nodes: [], edges: [] })
  const [activeId, setActiveId] = useState<string | null>(null)
  const [detailId, setDetailId] = useState<string | null>(null)
  const [detailLanguage, setDetailLanguage] = useState<'en' | 'ko'>('en')
  const [query, setQuery] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [showIngest, setShowIngest] = useState(false)
  const [form, setForm] = useState({ type: 'Concept', title: '', description: '', tags: '', resource: '', body: '# 개요\n\n' })

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
  const detail = documents.find((doc) => doc.id === detailId)
  const groups = useMemo(() => groupOrder.map(type => ({ type, label: typeLabel(type), docs: documents.filter(doc => doc.type === type) })).filter(group => group.docs.length), [documents])
  const selectDocument = (id: string, openDetail = false) => { setActiveId(id); if (openDetail) { setDetailLanguage('en'); setDetailId(id) } }

  return <main className="app-shell">
    <aside className="sidebar" aria-label="문서 탐색 사이드바">
      <div className="brand"><span className="brand-mark">K</span><span>Knowledge<br/><b>Wiki</b></span></div>
      <button className="home-button" onClick={() => { setActiveId(documents[0]?.id ?? null); setDetailId(null) }}>▦ 지식 공간</button>
      <div className="sidebar-heading"><span>문서 탐색</span><small>{documents.length}</small></div>
      <nav className="document-nav" aria-label="문서 그룹">
        {groups.map(group => <section className="document-group" key={group.type}><div className="group-title"><span>{group.label}</span><small>{group.docs.length}</small></div>{group.docs.map(doc => <button aria-current={doc.id === active?.id ? 'page' : undefined} className={doc.id === active?.id ? 'document-link selected' : 'document-link'} key={doc.id} onClick={() => selectDocument(doc.id, true)} title={doc.title}>{doc.title}</button>)}</section>)}
      </nav>
      <div className="sidebar-footer"><span className="status-dot"/> 인덱스 연결됨<br/><small>Markdown이 정본입니다</small></div>
    </aside>
    <section className="workspace">
      <header><div><p className="eyebrow">LOCAL KNOWLEDGE SYSTEM</p><h1>지식 작업 공간</h1><p className="header-copy">문서를 탐색하고, 연결을 확인하고, 로컬 지식을 관리하세요.</p></div><div className="header-actions"><button className="quiet-button" onClick={() => window.location.reload()}>↻ 인덱스 새로고침</button><button className="primary-button" onClick={() => setShowIngest(true)}>＋ 문서 추가</button></div></header>
      <div className="metric-row"><div className="metric"><span>전체 문서</span><strong>{documents.length}</strong></div><div className="metric"><span>문서 연결</span><strong>{graph.edges.length}</strong></div><div className="metric"><span>문서 형식</span><strong>OKF</strong></div><div className="metric"><span>검색 인덱스</span><strong>준비됨</strong></div></div>
      {error && <div className="error">{error}</div>}
      <div className="content-grid"><section className="panel graph-panel"><div className="panel-title"><div><p className="eyebrow">RELATIONSHIP MAP</p><h2>지식 그래프</h2></div><span className="pill">노드 {graph.nodes.length}개</span></div><GraphView graph={graph} activeId={active?.id ?? null} select={(id) => selectDocument(id, true)}/><p className="hint">노드를 선택하면 읽기 쉬운 상세 문서가 열립니다.</p></section>
      <section className="panel document-panel">{active ? <><div className="document-type">{typeLabel(active.type)}</div><h2>{active.title}</h2><p className="description">{active.description}</p><div className="tags">{active.tags.map(tag => <span key={tag}>#{tag}</span>)}</div><p className="document-summary">본문, 표, 코드, 메타데이터와 연결 문서를 상세 보기에서 읽을 수 있습니다.</p><button className="primary-button detail-button" onClick={() => setDetailId(active.id)}>문서 상세 보기</button><div className="document-footer"><code>{active.id}.md</code>{active.resource && <a href={active.resource} target="_blank" rel="noreferrer">원문 보기 ↗</a>}</div></> : <div className="empty">아직 문서가 없습니다. 첫 OKF 문서를 추가하세요.</div>}</section></div>
      <section className="panel list-panel"><div className="panel-title"><div><p className="eyebrow">BROWSE</p><h2>문서 목록</h2></div><input aria-label="문서 검색" placeholder="제목, 설명, 태그 검색…" value={query} onChange={event => setQuery(event.target.value)} /></div><div className="concept-list">{filtered.map(doc => <button className={doc.id === active?.id ? 'concept-card selected' : 'concept-card'} key={doc.id} onClick={() => selectDocument(doc.id, true)}><span className="card-type">{typeLabel(doc.type)}</span><strong>{doc.title}</strong><p>{doc.description}</p><span className="card-path">{doc.id}.md</span></button>)}</div></section>
      {detail && <div className="detail-backdrop" onMouseDown={() => setDetailId(null)}><section className="detail-dialog" role="dialog" aria-modal="true" aria-label={`${detailLanguage === 'ko' && detail.title_ko ? detail.title_ko : detail.title} 상세 문서`} onMouseDown={event => event.stopPropagation()}><header className="detail-header"><div><div className="document-type">{typeLabel(detail.type)}</div><h2>{detailLanguage === 'ko' && detail.title_ko ? detail.title_ko : detail.title}</h2><p className="description">{detailLanguage === 'ko' && detail.description_ko ? detail.description_ko : detail.description}</p></div><button className="close-button" aria-label="상세 문서 닫기" onClick={() => setDetailId(null)}>×</button></header><div className="detail-toolbar" aria-label="문서 언어"><button className={detailLanguage === 'ko' ? 'language-button active' : 'language-button'} disabled={!detail.body_ko} onClick={() => setDetailLanguage('ko')}>한국어</button><button className={detailLanguage === 'en' ? 'language-button active' : 'language-button'} onClick={() => setDetailLanguage('en')}>English</button></div><div className="detail-meta"><code>{detail.id}.md</code>{detail.timestamp && <span>갱신 {detail.timestamp}</span>}{detail.resource && <a href={detail.resource} target="_blank" rel="noreferrer">원문 보기 ↗</a>}</div><div className="tags">{detail.tags.map(tag => <span key={tag}>#{tag}</span>)}</div><article className="markdown-document"><MarkdownView body={detailLanguage === 'ko' && detail.body_ko ? detail.body_ko : detail.body}/></article>{detail.links.length > 0 && <section className="related-documents"><h3>연결 문서</h3>{detail.links.map(link => { const linked = documents.find(doc => doc.id === link); return <button key={link} onClick={() => selectDocument(link, true)}>{linked?.title ?? link}</button> })}</section>}</section></div>}
      {showIngest && <div className="modal-backdrop"><form className="ingest-form" onSubmit={submitIngest}><div className="panel-title"><div><p className="eyebrow">CREATE OKF DOCUMENT</p><h2>문서 추가</h2></div><button aria-label="문서 추가 닫기" type="button" className="close-button" onClick={() => setShowIngest(false)}>×</button></div><label>문서 제목<input aria-label="문서 제목" required value={form.title} onChange={event => setForm({ ...form, title: event.target.value })}/></label><label>유형<input value={form.type} onChange={event => setForm({ ...form, type: event.target.value })}/></label><label>설명<input value={form.description} onChange={event => setForm({ ...form, description: event.target.value })}/></label><label>태그 <small>(쉼표로 구분)</small><input value={form.tags} onChange={event => setForm({ ...form, tags: event.target.value })}/></label><label>원문 URL<input type="url" value={form.resource} onChange={event => setForm({ ...form, resource: event.target.value })}/></label><label>Markdown 본문<textarea aria-label="Markdown 본문" required value={form.body} onChange={event => setForm({ ...form, body: event.target.value })}/></label><button className="primary-button" type="submit">OKF 문서 저장</button></form></div>}
    </section>
  </main>
}
