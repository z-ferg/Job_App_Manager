import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Icon from '../components/Icon.jsx';
import { signup } from '../api/auth.js';

export default function Signup() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
    name: '',
    email: '',
    university: 'Virginia Tech',
    major: '',
    grad_year: '',
    password: '',
    });
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

    const createAccount = async (e) => {
    e.preventDefault();
    setError(null);
    if (form.password !== confirm) {
        setError('Passwords do not match.');
        return;
    }
    setLoading(true);
    try {
        await signup({ ...form, grad_year: Number(form.grad_year) });
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
          <h1 className="login__title">Start tracking your job search.</h1>
          <p className="login__lead">
            Create an account to keep every application, career fair, and follow-up in one place.
          </p>
        </div>

        <p className="login__footnote">For current Virginia Tech students.</p>
      </section>

      <section className="login__panel">
        <form className="login__form" onSubmit={createAccount}>
          <div className="stack-8">
            <h2 className="login__form-title">Create an account</h2>
            <p className="muted">It only takes a minute.</p>
          </div>

          <div className="field">
            <label htmlFor="name">Full name</label>
            <input
              id="name"
              autoComplete="name"
              required
              value={form.name}
              onChange={update('name')}
            />
          </div>

          <div className="field">
            <label htmlFor="email">VT email</label>
            <input
              id="email"
              type="email"
              placeholder="pid@vt.edu"
              autoComplete="email"
              required
              value={form.email}
              onChange={update('email')}
            />
          </div>

          <div className="field">
            <label htmlFor="university">University</label>
            <input
              id="university"
              required
              value={form.university}
              onChange={update('university')}
            />
          </div>

          <div className="field">
            <label htmlFor="major">Major</label>
            <input
              id="major"
              required
              value={form.major}
              onChange={update('major')}
            />
          </div>

          <div className="field">
            <label htmlFor="grad_year">Graduation year</label>
            <input
              id="grad_year"
              type="number"
              min="2000"
              max="2100"
              placeholder="2027"
              required
              value={form.grad_year}
              onChange={update('grad_year')}
            />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              minLength={8}
              required
              value={form.password}
              onChange={update('password')}
            />
          </div>

          <div className="field">
            <label htmlFor="confirm">Confirm password</label>
            <input
              id="confirm"
              type="password"
              autoComplete="new-password"
              required
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </div>

          {error && <p className="muted" role="alert">{error}</p>}

          <button type="submit" className="btn btn--outline btn--lg" disabled={loading}>
            {loading ? 'Creating account…' : 'Create account'}
          </button>

          <p className="login__signup">
            Already have an account? <Link to="/">Sign in</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
