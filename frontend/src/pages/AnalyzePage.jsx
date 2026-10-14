import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, formatDate, formatSize } from '../api.js'

const MAX_BYTES = 5 * 1024 * 1024
const ALLOWED = ['.pdf', '.docx', '.txt']
export default function AnalyzePage() {
  const navigate = useNavigate(), fileInput = useRef(null)
  const [docs, setDocs] = useState(null), [selected, setSelected] = useState(''), [title, setTitle] = useState(''), [jd, setJd] = useState('')
  const [uploading, setUploading] = useState(false), [uploadError, setUploadError] = useState(''), [running, setRunning] = useState(false), [error, setError] = useState(''), [dragging, setDragging] = useState(false)
  useEffect(() => { api.listDocuments().then((list) => { setDocs(list); if (list.length) setSelected(list[0].id) }).catch((err) => setError(err.message)) }, [])
  async function upload(file) {
    if (!file) return
    setUploadError('')
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
    if (!ALLOWED.includes(ext)) return setUploadError('Choose a PDF, DOCX or TXT file.')
    if (file.size > MAX_BYTES) return setUploadError('That file is larger than 5 MB.')
    setUploading(true)
    try { const doc = await api.uploadDocument(file); setDocs((current) => [doc, ...(current || [])]); setSelected(doc.id) }
    catch (err) { setUploadError(err.message) } finally { setUploading(false) }
  }
  async function onFile(event) { const file = event.target.files[0]; event.target.value = ''; await upload(file) }
  async function remove(doc) {
    if (!window.confirm(`Delete "${doc.original_filename}" and every analysis made from it?`)) return
    try { await api.deleteDocument(doc.id); const rest = docs.filter((d) => d.id !== doc.id); setDocs(rest); if (selected === doc.id) setSelected(rest[0]?.id || '') }
    catch (err) { setUploadError(err.message) }
  }
  async function analyze(event) {
    event.preventDefault(); setError(''); setRunning(true)
    try { const result = await api.createAnalysis({ document_id: selected, job_title: title.trim() || null, job_description: jd }); navigate(`/analyses/${result.id}`) }
    catch (err) { setError(err.message); setRunning(false) }
  }
  return <div className="analyze-page">
    <section className="welcome-banner"><div className="welcome-copy"><span className="eyebrow"><span className="sparkle">✦</span> YOUR CAREER, WITH CLARITY</span><h1>Find your <em>fit.</em></h1><p>Get a clearer picture of how your resume aligns with the role you want next.</p><div className="welcome-points"><span><b>01</b> Add your resume</span><span><b>02</b> Paste a job post</span><span><b>03</b> See your fit</span></div></div><div className="banner-art" aria-hidden="true"><div className="orbit orbit-a"/><div className="orbit orbit-b"/><div className="art-paper"><div className="paper-mark">R<span>IQ</span></div><div className="paper-line long"/><div className="paper-line medium"/><div className="paper-rule"/><div className="paper-line short"/><div className="paper-line medium"/><div className="paper-line long"/><div className="paper-check">✓</div></div><div className="art-bubble bubble-score"><span>↗</span><strong>Better prepared</strong><small>One step at a time</small></div><div className="art-bubble bubble-star">✦</div></div></section>
    <div className="section-heading"><div><span className="eyebrow">LET’S GET STARTED</span><h2>Build your match report</h2><p>Everything you need to take the guesswork out of applying.</p></div><div className="secure-pill"><span className="privacy-dot"/> Private by design</div></div>
    <div className="workflow-grid">
      <section className="workflow-card resume-card" aria-labelledby="docs-h"><div className="step-heading"><span className="step-number">01</span><div><h2 id="docs-h">Your resume</h2><p>Choose the version you want to put forward.</p></div></div>
        <button className={`dropzone ${dragging ? 'is-dragging' : ''}`} onClick={() => fileInput.current?.click()} onDragOver={(e) => { e.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); upload(e.dataTransfer.files[0]) }} disabled={uploading} type="button"><span className="upload-icon">↑</span><strong>{uploading ? 'Uploading your resume…' : 'Drop your resume here'}</strong><span>or <u>browse files</u> to upload</span><small>PDF, DOCX or TXT · 5 MB max</small></button>
        <input ref={fileInput} type="file" accept=".pdf,.docx,.txt" onChange={onFile} hidden />
        {uploadError && <p className="error" role="alert">{uploadError}</p>}
        <div className="saved-heading"><span>YOUR SAVED RESUMES</span><span className="count-pill">{docs?.length ?? '…'}</span></div>
        {docs === null && <div className="skeleton-row"><span/><div><i/><i/></div></div>}
        {docs?.length === 0 && <div className="empty-resumes"><span>▤</span><strong>No resume uploaded yet</strong><p>Your uploaded files will appear here.</p></div>}
        <ul className="doclist">{docs?.map((doc) => <li key={doc.id} className={selected === doc.id ? 'selected-doc' : ''}><label className="doc"><input type="radio" name="doc" checked={selected === doc.id} onChange={() => setSelected(doc.id)} /><span className="file-type">{doc.original_filename.toLowerCase().endsWith('.pdf') ? 'PDF' : doc.original_filename.toLowerCase().endsWith('.docx') ? 'DOC' : 'TXT'}</span><span className="doc-info"><span className="doc-name">{doc.original_filename}</span><span className="doc-meta">{formatSize(doc.size_bytes)} · expires {formatDate(doc.expires_at)}</span></span></label><button className="icon-button delete-doc" onClick={() => remove(doc)} aria-label={`Delete ${doc.original_filename}`} title="Delete resume">×</button></li>)}</ul>
        <div className="privacy-note"><span>♧</span><p><strong>Your resume stays yours.</strong><br />Files are automatically deleted after the retention period.</p></div>
      </section>
      <section className="workflow-card job-card" aria-labelledby="jd-h"><div className="step-heading"><span className="step-number">02</span><div><h2 id="jd-h">The role you want</h2><p>Give us the job posting to compare against.</p></div></div>
        <form onSubmit={analyze} className="job-form"><label>Job title <span className="optional">OPTIONAL</span><input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} placeholder="e.g. Backend Engineer" /></label>
          <label>Job description <span className="required-label">REQUIRED</span><textarea value={jd} onChange={(e) => setJd(e.target.value)} rows={10} minLength={30} maxLength={20000} required placeholder={'Paste the job description here…\n\nInclude responsibilities, requirements and nice-to-have skills for a more useful comparison.'} /><span className="textarea-footer"><span>{jd.length.toLocaleString()} / 20,000 characters</span><span className={jd.trim().length >= 30 ? 'valid-length' : ''}>{jd.trim().length >= 30 ? '✓ Ready to analyze' : `${Math.max(0, 30 - jd.trim().length)} more characters needed`}</span></span></label>
          {error && <p className="error" role="alert">{error}</p>}
          <button className="primary analyze-button" disabled={!selected || running || jd.trim().length < 30}>{running ? <><span className="button-spinner"/> Analyzing your match…</> : <>Analyze my fit <span aria-hidden="true">↗</span></>}</button>
          {!selected && <p className="form-note">↑ Upload or select a resume to continue.</p>}
          <p className="form-note">✦ Your report includes skill matches, gaps and relevant resume evidence.</p>
        </form>
      </section>
    </div>
    <div className="bottom-tip"><span className="tip-icon">✦</span><p><strong>A little tip</strong><br />Use the complete job description, not just the summary. The more context you share, the more useful your match report can be.</p></div>
  </div>
}
