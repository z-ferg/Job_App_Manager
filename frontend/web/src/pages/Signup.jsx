import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Icon from '../components/Icon.jsx';

export default function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const signUp = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Connects directly to your Python FastAPI backend
      const response = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to create account. Please try again.');
      }

      // Automatically redirect to login page upon success
      navigate('/login');
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
        <form className="login__form" onSubmit={signUp}>
          <div className="stack-8">
            <h2 className="login__form-title">Create an account</h2>
            <p className="muted">Join your fellow Hokies.</p>
          </div>

          <div className="field">
            <label htmlFor="first_name">First Name</label>
            <input
              id="first_name"
              name="first_name"
              type="text"
              placeholder="Hokie"
              required
              value={formData.first_name}
              onChange={handleChange}
            />
          </div>

          <div className="field">
            <label htmlFor="last_name">Last Name</label>
            <input
              id="last_name"
              name="last_name"
              type="text"
              placeholder="Bird"
              required
              value={formData.last_name}
              onChange={handleChange}
            />
          </div>

          <div className="field">
            <label htmlFor="email">VT email</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="pid@vt.edu"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <div className="field">
            <div className="field__row">
              <label htmlFor="password">Password</label>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleChange}
            />
          </div>

          {error && <p className="muted" role="alert" style={{ color: 'red' }}>{error}</p>}

          <button type="submit" className="btn btn--outline btn--lg" disabled={loading}>
            {loading ? 'Creating account…' : 'Sign up'}
          </button>

          <p className="login__signup">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </form>
      </section>
    </div>
  );
}