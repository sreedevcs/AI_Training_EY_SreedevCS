
from psycopg import Connection


def assign_ticket(
    conn: Connection,
    ticket_id: int,
    staff_id: int,
    assigned_by: int
):
    with conn.cursor() as cur:

        # Verify ticket exists
        cur.execute(
            """
            SELECT ticket_id
            FROM tickets
            WHERE ticket_id = %s
            """,
            (ticket_id,)
        )

        if cur.fetchone() is None:
            return {"error": "TICKET_NOT_FOUND"}

        # Verify support staff exists and is active
        cur.execute(
            """
            SELECT ss.staff_id
            FROM support_staff ss
            JOIN users u ON ss.user_id = u.user_id
            WHERE ss.staff_id = %s
              AND u.role = 'SUPPORT'
              AND u.is_active = TRUE
            """,
            (staff_id,)
        )

        if cur.fetchone() is None:
            return {"error": "STAFF_NOT_FOUND"}

        # Verify assigning user is an active support user or admin
        cur.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = %s
              AND role IN ('SUPPORT', 'ADMIN')
              AND is_active = TRUE
            """,
            (assigned_by,)
        )

        if cur.fetchone() is None:
            return {"error": "ASSIGNER_NOT_FOUND"}

        # Check for an existing active assignment
        cur.execute(
            """
            SELECT assignment_id
            FROM ticket_assignments
            WHERE ticket_id = %s
              AND assignment_status = 'ACTIVE'
            """,
            (ticket_id,)
        )

        if cur.fetchone() is not None:
            return {"error": "ALREADY_ASSIGNED"}

        # Create assignment
        cur.execute(
            """
            INSERT INTO ticket_assignments (
                ticket_id,
                staff_id,
                assigned_by
            )
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (ticket_id, staff_id, assigned_by)
        )

        assignment = cur.fetchone()

        # Record ticket activity
        cur.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                performed_by,
                activity_type,
                comment
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                ticket_id,
                assigned_by,
                "TICKET_ASSIGNED",
                f"Ticket assigned to support staff ID {staff_id}"
            )
        )

        # Record user activity
        cur.execute(
            """
            INSERT INTO user_activity (
                user_id,
                activity_type,
                description,
                ticket_id
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                assigned_by,
                "TICKET_ASSIGNED",
                f"Assigned ticket #{ticket_id} to staff ID {staff_id}",
                ticket_id
            )
        )

        return assignment


def reassign_ticket(
    conn: Connection,
    ticket_id: int,
    new_staff_id: int,
    reassigned_by: int
):
    with conn.cursor() as cur:

        # Lock the ticket row
        cur.execute(
            """
            SELECT ticket_id
            FROM tickets
            WHERE ticket_id = %s
            FOR UPDATE
            """,
            (ticket_id,)
        )

        if cur.fetchone() is None:
            return {"error": "TICKET_NOT_FOUND"}

        # Verify the user performing the reassignment
        cur.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE user_id = %s
              AND is_active = TRUE
              AND role IN ('SUPPORT', 'ADMIN')
            """,
            (reassigned_by,)
        )

        actor = cur.fetchone()

        if actor is None:
            return {"error": "INVALID_ACTOR"}

        # A support user can transfer only a ticket assigned to them
        if actor["role"] == "SUPPORT":
            cur.execute(
                """
                SELECT ss.staff_id
                FROM support_staff ss
                JOIN ticket_assignments ta
                    ON ta.staff_id = ss.staff_id
                WHERE ss.user_id = %s
                  AND ta.ticket_id = %s
                  AND ta.assignment_status = 'ACTIVE'
                """,
                (reassigned_by, ticket_id)
            )

            if cur.fetchone() is None:
                return {"error": "NOT_ASSIGNED"}

        # Verify the new staff member
        cur.execute(
            """
            SELECT ss.staff_id
            FROM support_staff ss
            JOIN users u ON u.user_id = ss.user_id
            WHERE ss.staff_id = %s
              AND u.role = 'SUPPORT'
              AND u.is_active = TRUE
            """,
            (new_staff_id,)
        )

        if cur.fetchone() is None:
            return {"error": "STAFF_NOT_FOUND"}

        # Find the current active assignment
        cur.execute(
            """
            SELECT assignment_id, staff_id
            FROM ticket_assignments
            WHERE ticket_id = %s
              AND assignment_status = 'ACTIVE'
            FOR UPDATE
            """,
            (ticket_id,)
        )

        old_assignment = cur.fetchone()

        if old_assignment is None:
            return {"error": "NO_ACTIVE_ASSIGNMENT"}

        old_staff_id = old_assignment["staff_id"]

        if old_staff_id == new_staff_id:
            return {"error": "SAME_STAFF"}

        # Mark the old assignment as transferred
        cur.execute(
            """
            UPDATE ticket_assignments
            SET assignment_status = 'TRANSFERRED',
                unassigned_at = CURRENT_TIMESTAMP
            WHERE assignment_id = %s
            """,
            (old_assignment["assignment_id"],)
        )

        # Create the new active assignment
        cur.execute(
            """
            INSERT INTO ticket_assignments (
                ticket_id,
                staff_id,
                assigned_by
            )
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (ticket_id, new_staff_id, reassigned_by)
        )

        new_assignment = cur.fetchone()

        # Record ticket activity
        cur.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                performed_by,
                activity_type,
                comment
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                ticket_id,
                reassigned_by,
                "TICKET_REASSIGNED",
                f"Ticket transferred from staff ID {old_staff_id} "
                f"to staff ID {new_staff_id}"
            )
        )

        # Record user activity
        cur.execute(
            """
            INSERT INTO user_activity (
                user_id,
                activity_type,
                description,
                ticket_id
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                reassigned_by,
                "TICKET_REASSIGNED",
                f"Reassigned ticket #{ticket_id} "
                f"from staff ID {old_staff_id} "
                f"to staff ID {new_staff_id}",
                ticket_id
            )
        )

        return new_assignment


def get_ticket_assignments(conn, ticket_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                ta.assignment_id,
                ta.ticket_id,
                ta.staff_id,
                ta.assigned_by,
                ta.assigned_at,
                ta.unassigned_at,
                ta.assignment_status,
                u.full_name AS staff_name,
                u.email AS staff_email
            FROM ticket_assignments ta
            JOIN support_staff ss
                ON ta.staff_id = ss.staff_id
            JOIN users u
                ON ss.user_id = u.user_id
            WHERE ta.ticket_id = %s
            ORDER BY ta.assigned_at ASC, ta.assignment_id ASC
            """,
            (ticket_id,)
        )

        return cur.fetchall()
