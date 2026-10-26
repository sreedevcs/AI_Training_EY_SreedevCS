import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const location = useLocation()
  const navigate = useNavigate()

  function handleSubmit(event) {
    event.preventDefault()

    onLogin()

    const destination = location.state?.from?.pathname || '/'
    navigate(destination, { replace: true })
  }

  return (
    <main>
      <h1>Log in</h1>
      <p>Please enter your credentials</p>

      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        <button type="submit">Log in</button>
      </form>

      <p><Link to="/">Back to home</Link></p>
    </main>
  )
}

export default Login