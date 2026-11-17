// A row of toggle pills. `options` is [{ value, label, count? }].
export default function FilterPills({ options, value, onChange, label }) {
  return (
    <div className="pills" role="group" aria-label={label}>
      {options.map((opt) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            className={`pill${active ? ' pill--active' : ''}`}
            aria-pressed={active}
            onClick={() => onChange(opt.value)}
          >
            {opt.label}
            {opt.count != null && <span className="pill__count">{opt.count}</span>}
          </button>
        );
      })}
    </div>
  );
}
