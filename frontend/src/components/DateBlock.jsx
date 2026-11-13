import { dayOfMonth, monthAbbr } from '../utils/dates.js';

export default function DateBlock({ date, large = false }) {
  return (
    <span className={`date-block${large ? ' date-block--lg' : ''}`}>
      <span className="date-block__month">{monthAbbr(date)}</span>
      <span className="date-block__day">{dayOfMonth(date)}</span>
    </span>
  );
}
