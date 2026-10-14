import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, formatDate } from '../api.js'
import CoverageStrip from '../components/CoverageStrip.jsx'

function SkillChips({ skills, tone }) {
  if (!skills.length) return <p className="hint">None.</p>
  return (
    <ul className="chips">
      {skills.map((s) => (
        <li key={s.name} className={tone} title={s.category}>{s.name}</li>
      ))}
    </ul>
  )
}

export default function ReportPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getAnalysis(id).then(setAnalysis).catch((err) => setError(err.message))
  }, [id])

  async function remove() {
    if (!window.confirm('Delete this analysis?')) return
    try {
      await api.deleteAnalysis(id)
      navigate('/history')
    } catch (err) {
      setError(err.message)
    }
  }

  if (error) return <p className="error" role="alert">{error} <Link to="/history">Back to history</Link></p>
  if (!analysis) return <p className="hint">Loading…</p>

  const { report } = analysis
  const reqMissing = report.missing_skills.filter((s) => s.importance === 'required')
  const prefMissing = report.missing_skills.filter((s) => s.importance === 'preferred')
  const exp = report.experience

  return (
    <article className="report">
      <p className="crumb"><Link to="/history">← History</Link></p>
      <header className="report-head">
        <div>
          <h1>{analysis.job_title || 'Untitled role'}</h1>
          <p className="hint">{analysis.document_filename} · analyzed {formatDate(analysis.created_at)}</p>
        </div>
        <div className="score">
          <span className="score-num">{Math.round(report.match_score)}</span>
          <span className="score-unit">% match<br /><small>required skills count double</small></span>
        </div>
      </header>

      <CoverageStrip matched={report.matched_skills} missing={report.missing_skills} />

      {report.warnings.length > 0 && (
        <ul className="warnings">{report.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
      )}

      <div className="grid">
        <section className="card">
          <h2>Missing required skills</h2>
          <SkillChips skills={reqMissing} tone="bad" />
          {prefMissing.length > 0 && (
            <>
              <h3>Missing nice-to-haves</h3>
              <SkillChips skills={prefMissing} tone="soft" />
            </>
          )}
        </section>

        <section className="card">
          <h2>Skills you match</h2>
          <SkillChips skills={report.matched_skills} tone="ok" />
        </section>

        <section className="card">
          <h2>Experience</h2>
          {exp.estimated_years === null ? (
            <p className="hint">No dated roles found, so years of experience could not be estimated.</p>
          ) : (
            <p>
              About <strong>{exp.estimated_years} years</strong> from dated roles on the resume
              {exp.required_years !== null && (
                <>
                  ; the posting asks for <strong>{exp.required_years}+</strong>
                  {exp.meets_requirement ? ' — you meet that.' : ' — you fall short of that.'}
                </>
              )}
            </p>
          )}
        </section>

        <section className="card">
          <h2>Words the posting repeats that your resume does not</h2>
          {report.missing_keywords.length ? (
            <ul className="chips">{report.missing_keywords.map((k) => <li key={k} className="soft">{k}</li>)}</ul>
          ) : (
            <p className="hint">No repeated keywords are missing.</p>
          )}
        </section>

        <section className="card wide">
          <h2>Where your resume already shows relevant skills</h2>
          {report.relevant_experience.length ? (
            <ul className="evidence">{report.relevant_experience.map((l, i) => <li key={i}>{l}</li>)}</ul>
          ) : (
            <p className="hint">No lines mentioning the job's skills were found in your experience or projects.</p>
          )}
        </section>

        {report.additional_skills.length > 0 && (
          <section className="card wide">
            <h2>Other skills on your resume</h2>
            <SkillChips skills={report.additional_skills} tone="neutral" />
          </section>
        )}
      </div>

      <p className="report-foot">
        Matching is rule-based and uses a fixed skill list, so unusual spellings can be missed.
        <button className="link danger" onClick={remove}>Delete this analysis</button>
      </p>
    </article>
  )
}
