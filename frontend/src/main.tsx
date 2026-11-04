import { FormEvent, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type Project = { id: string; name: string; description: string }

const api = (path: string, token = '') => fetch(`/v1${path}`, {
  headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }
})

function App() {
  const [token, setToken] = useState('')
  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const [projects, setProjects] = useState<Project[]>([])
  const [message, setMessage] = useState('Sign in to manage requirements and review-safe test scenarios.')
  const [projectName, setProjectName] = useState('Synthetic login')

  async function signIn(event: FormEvent) {
    event.preventDefault()
    const response = await fetch('/v1/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: user, password }) })
    if (!response.ok) return setMessage('Sign-in failed. Use the locally bootstrapped account.')
    const data = await response.json(); setToken(data.access_token); setMessage(`Signed in as ${data.user.display_name} (${data.user.role}).`)
    setProjects(await (await api('/projects', data.access_token)).json())
  }

  async function createProject() {
    const response = await fetch('/v1/projects', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ name: projectName, description: 'Synthetic authorised QA demonstration project.' }) })
    if (response.ok) { setProjects([await response.json(), ...projects]); setMessage('Project created. Add a requirement through the API to generate reviewable cases.') }
    else setMessage('Only the authenticated developer can create projects.')
  }

  return <main>
    <header><div><span className="eyebrow">TESTFORGE AI</span><h1>Requirement-aware QA workspace</h1><p>Trace requirements to human-reviewed, controlled automation.</p></div><span className="pill">MVP • review first</span></header>
    {!token ? <section className="card auth"><h2>Sign in</h2><form onSubmit={signIn}><label>Account<select value={user} onChange={e => setUser(e.target.value)}><option value="">Choose account</option><option value="saritha">Saritha S · Developer</option><option value="swapin">Swapin Vidya · QA reviewer</option></select></label><label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} /></label><button>Sign in</button></form><p className="muted">Bootstrap credentials are supplied locally by the operator; no passwords are stored in the frontend.</p></section> : <>
      <section className="metrics"><div><strong>{projects.length}</strong><span>Projects</span></div><div><strong>Draft-first</strong><span>Review policy</span></div><div><strong>0</strong><span>Unverified executions</span></div></section>
      <section className="grid"><div className="card"><div className="section-title"><h2>Projects</h2><span className="status approved">authenticated</span></div><label>New project name<input value={projectName} onChange={e => setProjectName(e.target.value)} /></label><button onClick={createProject}>Create project</button>{projects.length === 0 ? <p className="muted">No projects yet.</p> : <ul>{projects.map(project => <li key={project.id}><b>{project.name}</b><small>{project.id}</small></li>)}</ul>}</div><div className="card"><div className="section-title"><h2>Workflow guardrails</h2><span className="status draft">active</span></div><p>Generated scenarios begin as <b>draft</b>, move through <b>submitted</b>, and require QA approval before controlled export.</p><p>Execution is limited to the bundled synthetic application and remains disabled unless the operator explicitly enables it.</p><div className="legend"><span className="status draft">draft</span><span className="status submitted">submitted</span><span className="status approved">approved</span><span className="status rejected">rejected</span></div></div></section>
    </>}
    <footer>{message}</footer>
  </main>
}

createRoot(document.getElementById('root')!).render(<App />)
