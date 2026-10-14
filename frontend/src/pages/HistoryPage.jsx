import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, formatDate } from '../api.js'

export default function HistoryPage() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  useEffect(() => { api.listAnalyses().then(setItems).catch((err) => setError(err.message)) }, [])
  const filtered = useMemo(() => (items || []).filter((a) => `${a.job_title || ''} ${a.document_filename || ''}`.toLowerCase().includes(query.toLowerCase().trim())), [items, query])
  return <section aria-labelledby="hist-h">
    <header className="history-head"><div><span className="eyebrow">YOUR PROGRESS, ALL IN ONE PLACE</span><h1 id="hist-h">Analysis history</h1><p>Revisit your reports and keep track of every opportunity.</p></div><Link className="primary" to="/">＋ New analysis</Link></header>
    {error && <p className="error" role="alert">{error}</p>}
    {items && items.length > 0 && <div className="history-tools"><label className="history-search"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by role or resume name…" aria-label="Search analysis history" /></label><span className="history-count">Showing {filtered.length} of {items.length} {items.length === 1 ? 'report' : 'reports'}</span></div>}
    {items === null && !error && <div className="card empty-resumes"><span className="loading-orb"/><strong>Gathering your reports…</strong></div>}
    {items?.length === 0 && <div className="history-empty"><span className="empty-symbol">◷</span><strong>Your next opportunity starts here.</strong><p>When you run your first resume analysis, the report will be saved here.</p><Link className="primary" to="/">Analyze a resume <span>→</span></Link></div>}
    {items?.length > 0 && filtered.length === 0 && <div className="history-empty"><span className="empty-symbol">⌕</span><strong>No matching reports</strong><p>Try another job title or resume filename.</p><button className="link" onClick={() => setQuery('')}>Clear search</button></div>}
    <ul className="history">{filtered.map((a) => <li key={a.id}><Link to={`/analyses/${a.id}`}><span className="score-chip" data-level={a.match_score >= 70 ? 'high' : a.match_score >= 40 ? 'mid' : 'low'}>{Math.round(a.match_score)}%</span><span className="history-main"><strong>{a.job_title || 'Untitled role'}</strong><span>▤ &nbsp;{a.document_filename}</span></span><time>{formatDate(a.created_at)}</time><span className="history-arrow" aria-hidden="true">↗</span></Link></li>)}</ul>
  </section>
}
