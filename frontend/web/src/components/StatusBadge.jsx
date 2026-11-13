import { STATUSES, statusSlug } from '../data.js';

export default function StatusBadge({ status }) {
  return <span className={`badge badge--${statusSlug(status)}`}>{status}</span>;
}

// A badge-styled dropdown for changing an application's status in place.
export function StatusSelect({ status, onChange, disabled, label }) {
  return (
    <select
      className={`badge badge-select badge--${statusSlug(status)}`}
      value={status}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      aria-label={label}
    >
      {STATUSES.map((s) => <option key={s}>{s}</option>)}
    </select>
  );
}
