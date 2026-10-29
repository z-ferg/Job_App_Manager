import { Link, useNavigate } from 'react-router-dom';
import Icon from '../components/Icon.jsx';

export default function Login() {
  const navigate = useNavigate();

  // TODO: replace with VT CAS / SSO and real email auth.
  const signIn = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="login">
      <section className="login__hero">
        <div className="brand brand--hero">
          <span className="brand__mark brand__mark--lg">
            <Icon name="briefcase" size={26} />
          </span>
          <span className="brand__name brand__name--lg">Hokie Job Tracker</span>
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

          <button type="button" className="btn btn--primary btn--lg" onClick={signIn}>
            <Icon name="lock" />
            Sign in with VT PID
          </button>

          <div className="divider">or use your email</div>

          <div className="field">
            <label htmlFor="email">VT email</label>
            <input id="email" type="email" placeholder="pid@vt.edu" autoComplete="email" required />
          </div>

          <div className="field">
            <div className="field__row">
              <label htmlFor="password">Password</label>
              <a href="#" className="link-sm">Forgot password?</a>
            </div>
            <input id="password" type="password" autoComplete="current-password" required />
          </div>

          <label className="checkbox">
            <input type="checkbox" />
            Keep me signed in on this computer
          </label>

          <button type="submit" className="btn btn--outline btn--lg">Sign in</button>

          <p className="login__signup">
            New here? <Link to="/">Create an account</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
