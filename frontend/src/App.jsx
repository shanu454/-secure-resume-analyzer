import { useCallback, useEffect, useState } from 'react'
import { Navigate, NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import { api, getToken, setToken, setUnauthorizedHandler } from './api.js'
import AuthPage from './pages/AuthPage.jsx'
import AnalyzePage from './pages/AnalyzePage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import ReportPage from './pages/ReportPage.jsx'

function BrandMark() {
  return <span className="brand-mark" aria-hidden="true"><span>R</span></span>
}

export default function App() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(Boolean(getToken()))
  const [mobileNav, setMobileNav] = useState(false)

  const signOut = useCallback(() => {
    setToken(null)
    setUser(null)
    navigate('/login')
  }, [navigate])

  useEffect(() => { setUnauthorizedHandler(signOut) }, [signOut])
  useEffect(() => {
    if (!getToken()) return
    api.me().then(setUser).catch(() => setToken(null)).finally(() => setChecking(false))
  }, [])

  if (checking) return <div className="loading-screen"><span className="loading-orb" /><p>Preparing your workspace…</p></div>
  if (!user) return <Routes><Route path="/login" element={<AuthPage onSignedIn={setUser} />} /><Route path="*" element={<Navigate to="/login" replace />} /></Routes>

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand" aria-label="ResumeIQ home"><BrandMark /><span>resume<span className="brand-light">IQ</span><small>CAREER INTELLIGENCE</small></span></NavLink>
          <button className="mobile-menu" onClick={() => setMobileNav(!mobileNav)} aria-label="Toggle navigation" aria-expanded={mobileNav}>{mobileNav ? '✕' : '☰'}</button>
          <nav className={mobileNav ? 'nav-open' : ''} aria-label="Main">
            <NavLink to="/" end onClick={() => setMobileNav(false)}><span className="nav-icon">✳</span> New analysis</NavLink>
            <NavLink to="/history" onClick={() => setMobileNav(false)}><span className="nav-icon">◷</span> History</NavLink>
          </nav>
          <div className="who"><span className="avatar">{user.email?.charAt(0).toUpperCase() || 'U'}</span><span className="user-email">{user.email}</span><button className="signout" onClick={signOut} title="Sign out">↗</button></div>
        </div>
      </header>
      <main className="page"><Routes><Route path="/" element={<AnalyzePage />} /><Route path="/history" element={<HistoryPage />} /><Route path="/analyses/:id" element={<ReportPage />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></main>
      <footer className="app-footer"><span>✳ resumeIQ</span><span>Thoughtful tools for your next career move.</span><span><i className="privacy-dot" /> Your documents stay yours</span></footer>
    </div>
  )
}
