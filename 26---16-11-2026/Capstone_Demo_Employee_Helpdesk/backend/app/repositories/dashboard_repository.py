
def get_dashboard_summary(conn):

    query = """
        SELECT
            COUNT(*) AS total_tickets,

            COUNT(*) FILTER (
                WHERE status = 'OPEN'
            ) AS open_tickets,

            COUNT(*) FILTER (
                WHERE status = 'IN_PROGRESS'
            ) AS in_progress_tickets,

            COUNT(*) FILTER (
                WHERE status = 'RESOLVED'
            ) AS resolved_tickets,

            COUNT(*) FILTER (
                WHERE status = 'CLOSED'
            ) AS closed_tickets,

            COUNT(*) FILTER (
                WHERE priority = 'LOW'
            ) AS low_priority,

            COUNT(*) FILTER (
                WHERE priority = 'MEDIUM'
            ) AS medium_priority,

            COUNT(*) FILTER (
                WHERE priority = 'HIGH'
            ) AS high_priority,

            COUNT(*) FILTER (
                WHERE category = 'HARDWARE'
            ) AS hardware_tickets,

            COUNT(*) FILTER (
                WHERE category = 'SOFTWARE'
            ) AS software_tickets,

            COUNT(*) FILTER (
                WHERE category = 'NETWORK'
            ) AS network_tickets,

            COUNT(*) FILTER (
                WHERE category = 'ACCESS'
            ) AS access_tickets,

            COUNT(*) FILTER (
                WHERE category = 'OTHER'
            ) AS other_tickets

        FROM tickets;
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    return {
        "total_tickets": result["total_tickets"],

        "by_status": {
            "OPEN": result["open_tickets"],
            "IN_PROGRESS": result["in_progress_tickets"],
            "RESOLVED": result["resolved_tickets"],
            "CLOSED": result["closed_tickets"]
        },

        "by_priority": {
            "LOW": result["low_priority"],
            "MEDIUM": result["medium_priority"],
            "HIGH": result["high_priority"]
        },

        "by_category": {
            "HARDWARE": result["hardware_tickets"],
            "SOFTWARE": result["software_tickets"],
            "NETWORK": result["network_tickets"],
            "ACCESS": result["access_tickets"],
            "OTHER": result["other_tickets"]
        }
    }
