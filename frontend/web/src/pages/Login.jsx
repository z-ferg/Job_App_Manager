import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import { login } from '../api/auth.js';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // TODO: replace with VT CAS / SSO and real email auth.
  const signIn = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login">
      <section className="login__hero">
        <div className="brand brand--hero">
          <span className="brand__mark brand__mark--lg">
            <Icon name="briefcase" size={26} />
          </span>
          <span className="brand__name brand__name--lg">Job Application Manager</span>
        </div>

        <div className="login__pitch">
          <h1 className="login__title">Your job search, all in one place.</h1>
          <p className="login__lead">
            Built for Virginia Tech students to track applications, plan for career fairs, and stay on
            top of every follow-up.
          </p>
          <ul className="login__features">
            <li>
              <span className="login__feature-icon"><Icon name="briefcase" size={18} /></span>
              Every application and its status at a glance
            </li>
            <li>
              <span className="login__feature-icon"><Icon name="calendar" size={18} /></span>
              Upcoming career fairs on campus
            </li>
            <li>
              <span className="login__feature-icon"><Icon name="bell" size={18} /></span>
              Reminders for deadlines and follow-ups
            </li>
          </ul>
        </div>

        <p className="login__footnote">For current Virginia Tech students.</p>
      </section>

      <section className="login__panel">
        <form className="login__form" onSubmit={signIn}>
          <div className="stack-8">
            <h2 className="login__form-title">Sign in</h2>
            <p className="muted">Welcome back, Hokie.</p>
          </div>
          
          <div className="field">
            <label htmlFor="email">VT email</label>
            <input
              id="email"
              type="email"
              placeholder="pid@vt.edu"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="field">
            <div className="field__row">
              <label htmlFor="password">Password</label>
              <a href="#" className="link-sm">Forgot password?</a>
            </div>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <label className="checkbox">
            <input type="checkbox" />
            Keep me signed in on this computer
          </label>

          {error && <p className="muted" role="alert">{error}</p>}

          <button type="submit" className="btn btn--outline btn--lg" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

          <p className="login__signup">
            New here? <Link to="/signup">Create an account</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
