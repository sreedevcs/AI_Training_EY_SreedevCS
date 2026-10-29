function AttendanceCard({ title, value, subtitle, icon, color }) {
  return (
    <div className="attendance-card">
      <div className="attendance-card-header">
        <span>{title}</span>
        <span className={`attendance-card-icon ${color}`}>
          {icon}
        </span>
      </div>

      <h2>{value}</h2>
      <p>{subtitle}</p>
    </div>
  );
}

export default AttendanceCard;