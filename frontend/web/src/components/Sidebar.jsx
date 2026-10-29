import { Link, NavLink } from 'react-router-dom';
import Icon from './Icon.jsx';
import { student } from '../data.js';

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: 'home' },
  { to: '/applications', label: 'Applications', icon: 'briefcase' },
  { to: '/fairs', label: 'Career fairs', icon: 'calendar' },
  { to: '/reminders', label: 'Reminders', icon: 'bell' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <Link to="/dashboard" className="brand">
        <span className="brand__mark">
          <Icon name="briefcase" size={22} />
        </span>
        <span className="brand__name">Hokie Job Tracker</span>
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
        <span className="profile__avatar">{student.initials}</span>
        <span className="profile__text">
          <span className="profile__name">{student.name}</span>
          <span className="profile__meta">
            {student.major} · Class of {student.classYear}
          </span>
        </span>
        <Link to="/" className="profile__signout" aria-label="Sign out">
          <Icon name="logout" size={18} />
        </Link>
      </div>
    </aside>
  );
}
