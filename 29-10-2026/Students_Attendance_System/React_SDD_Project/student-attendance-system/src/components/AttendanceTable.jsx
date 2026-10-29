function AttendanceTable({ records }) {
  return (
    <div className="attendance-table-wrapper">
      <table className="attendance-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {records.length > 0 ? (
            records.map((record) => (
              <tr key={record.id}>
                <td>{record.date}</td>
                <td>
                  <span
                    className={`status-badge ${record.status.toLowerCase()}`}
                  >
                    {record.status}
                  </span>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="2">No attendance records available.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default AttendanceTable;