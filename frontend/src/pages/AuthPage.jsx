import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'

export default function AuthPage({ onSignedIn }) {
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event) {
    event.preventDefault(); setError(''); setBusy(true)
    try {
      if (mode === 'register') await api.register(email, password)
      await api.login(email, password); onSignedIn(await api.me()); navigate('/')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  const creating = mode === 'register'
  return (
    <main className="auth-layout">
      <section className="auth-showcase">
        <div className="auth-brand"><span className="brand-mark"><span>R</span></span><span>resume<span className="brand-light">IQ</span></span></div>
        <div className="showcase-copy"><span className="eyebrow"><span className="sparkle">✦</span> YOUR NEXT CHAPTER STARTS HERE</span><h1>Make your next<br />move <em>count.</em></h1><p>Turn job descriptions into a clear game plan. Know your strengths, spot the gaps, and show up with confidence.</p>
          <div className="preview-card"><div className="preview-top"><span className="preview-file">▤</span><div><strong>Product Engineer</strong><small>Resume match overview</small></div><span className="preview-status">ANALYZED</span></div><div className="preview-score-row"><div className="preview-ring"><span>82<small>%</small></span></div><div><strong>You're on the right track</strong><p>Strong alignment with this role</p></div></div><div className="preview-tags"><span>✓ Python</span><span>✓ APIs</span><span>↗ System design</span></div></div>
        </div>
        <div className="auth-bottom"><span>Built for ambitious careers.</span><span>✦ Clarity over guesswork</span></div>
        <div className="showcase-glow glow-one" /><div className="showcase-glow glow-two" />
      </section>
      <section className="auth-panel"><div className="auth-panel-inner"><div className="mobile-auth-brand"><span className="brand-mark"><span>R</span></span> resume<span className="brand-light">IQ</span></div><span className="eyebrow auth-eyebrow">{creating ? 'LET’S GET YOU STARTED' : 'WELCOME BACK'}</span><h2>{creating ? 'Create your account' : 'Good to see you again.'}</h2><p className="lede">{creating ? 'A smarter job search begins with a few details.' : 'Sign in to pick up where your career journey left off.'}</p>
          <form onSubmit={submit} className="auth-form">
            <label>Email address<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" placeholder="you@example.com" /></label>
            <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={creating ? 8 : undefined} autoComplete={creating ? 'new-password' : 'current-password'} placeholder={creating ? 'At least 8 characters' : 'Enter your password'} />{creating && <small>Use at least 8 characters.</small>}</label>
            {error && <p className="error" role="alert">{error}</p>}
            <button className="primary auth-submit" disabled={busy}>{busy ? <><span className="button-spinner" /> Please wait…</> : creating ? 'Create my account <' : 'Sign in to workspace'} <span aria-hidden="true">→</span></button>
          </form>
          <div className="auth-switch">{creating ? 'Already have an account?' : 'New to resumeIQ?'} <button className="link" onClick={() => { setMode(creating ? 'login' : 'register'); setError('') }}>{creating ? 'Sign in' : 'Create an account'}</button></div>
          <div className="auth-trust"><span>⌑</span><p><strong>Your career data deserves care.</strong><br />Resume files are automatically removed after the retention period.</p></div>
        </div><p className="auth-legal">By continuing, you agree to use resumeIQ responsibly. <span>© 2026 resumeIQ</span></p></section>
    </main>
  )
}
