import { Link, NavLink } from 'react-router-dom';
import Icon from './Icon.jsx';
import { getStudent, logout } from '../api/auth.js'

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: 'home' },
  { to: '/applications', label: 'Applications', icon: 'briefcase' },
  { to: '/fairs', label: 'Career fairs', icon: 'calendar' },
  { to: '/reminders', label: 'Reminders', icon: 'bell' },
];

export default function Sidebar() {
  // Read on every render so it reflects whoever is currently logged in.
  const student = getStudent()
  const name = student?.name ?? 'missing_name';
  const initials = student?.initials ?? name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  const gradYear = student?.grad_year ?? 'missing_year';
  const major = student?.major ?? 'missing_major';

  return (
    <aside className="sidebar">
      <Link to="/dashboard" className="brand">
        <span className="brand__mark">
          <Icon name="briefcase" size={22} />
        </span>
        <span className="brand__name">JAM</span>
      </Link>

      <nav aria-label="Main" className="sidebar__nav">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-link${isActive ? ' nav-link--active' : ''}`}
          >
            <Icon name={item.icon} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__spacer" />

      <div className="profile">
        <span className="profile__avatar">{initials}</span>
        <span className="profile__text">
          <span className="profile__name">{name}</span>
          <span className="profile__meta">
            {major} {gradYear % 100}'
          </span>
        </span>
        <Link to="/" onClick={logout} className="profile__signout" aria-label="Sign out">
          <Icon name="logout" size={18} />
        </Link>
      </div>
    </aside>
  );
}
