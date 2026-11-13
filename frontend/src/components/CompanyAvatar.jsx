export default function CompanyAvatar({ name, size = 'md' }) {
  return (
    <span className={`avatar avatar--${size}`} aria-hidden="true">
      {name.charAt(0)}
    </span>
  );
}
