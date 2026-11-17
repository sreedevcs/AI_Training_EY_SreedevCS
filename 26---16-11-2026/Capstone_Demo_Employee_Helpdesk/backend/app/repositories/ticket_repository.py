
from psycopg import Connection


def create_ticket(conn: Connection, ticket_data: dict):
    with conn.cursor() as cur:

        # Verify that the requester is an active employee
        cur.execute(
            """
            SELECT
                user_id,
                full_name AS requester_name,
                email AS requester_email
            FROM users
            WHERE user_id = %s
              AND role = 'EMPLOYEE'
              AND is_active = TRUE
            """,
            (ticket_data["requester_id"],)
        )

        requester = cur.fetchone()

        if requester is None:
            return None

        # Insert the ticket
        cur.execute(
            """
            INSERT INTO tickets (
                requester_id,
                title,
                description,
                category
            )
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (
                ticket_data["requester_id"],
                ticket_data["title"],
                ticket_data["description"],
                ticket_data["category"]
            )
        )

        ticket = cur.fetchone()
        ticket["requester_name"] = requester["requester_name"]
        ticket["requester_email"] = requester["requester_email"]

        # Record ticket creation in ticket_activity
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
                ticket["ticket_id"],
                ticket_data["requester_id"],
                "TICKET_CREATED",
                "Ticket created by employee"
            )
        )

        # Record the action in user_activity
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
                ticket_data["requester_id"],
                "TICKET_CREATED",
                f"Created ticket #{ticket['ticket_id']}",
                ticket["ticket_id"]
            )
        )

        return ticket



def get_all_tickets(
    conn: Connection,
    status=None,
    category=None,
    priority=None,
    requester_id=None,
    limit=100,
    offset=0
):
    query = """
        SELECT
            t.*,
            u.full_name AS requester_name,
            u.email AS requester_email
        FROM tickets t
        LEFT JOIN users u ON u.user_id = t.requester_id
    """
    conditions = []
    params = []

    if status:
        conditions.append("t.status = %s")
        params.append(status)

    if category:
        conditions.append("t.category = %s")
        params.append(category)

    if priority:
        conditions.append("t.priority = %s")
        params.append(priority)

    if requester_id:
        conditions.append("t.requester_id = %s")
        params.append(requester_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        ORDER BY t.created_at DESC
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])

    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        return cur.fetchall()





def get_ticket_by_id(conn: Connection, ticket_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                t.*,
                u.full_name AS requester_name,
                u.email AS requester_email
            FROM tickets t
            LEFT JOIN users u ON u.user_id = t.requester_id
            WHERE t.ticket_id = %s
            """,
            (ticket_id,)
        )

        return cur.fetchone()


from psycopg import Connection


def update_ticket(
    conn: Connection,
    ticket_id: int,
    update_data: dict
):
    with conn.cursor() as cur:

        # Check whether the ticket exists
        cur.execute(
            """
            SELECT
                t.*,
                u.full_name AS requester_name,
                u.email AS requester_email
            FROM tickets t
            LEFT JOIN users u ON u.user_id = t.requester_id
            WHERE t.ticket_id = %s
            """,
            (ticket_id,)
        )

        existing_ticket = cur.fetchone()

        if existing_ticket is None:
            return None

        # Keep only fields that were actually supplied
        allowed_fields = {"title", "description", "category"}

        updates = {
            key: value
            for key, value in update_data.items()
            if key in allowed_fields
        }

        if not updates:
            return existing_ticket

        # Update the ticket
        set_clause = ", ".join(
            f"{field} = %s" for field in updates
        )

        values = list(updates.values())
        values.append(ticket_id)

        cur.execute(
            f"""
            UPDATE tickets
            SET {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
            RETURNING *
            """,
            tuple(values)
        )

        updated_ticket = cur.fetchone()
        updated_ticket["requester_name"] = existing_ticket["requester_name"]
        updated_ticket["requester_email"] = existing_ticket["requester_email"]

        # Record ticket-specific activity
        if "category" in updates:
            cur.execute(
                """
                INSERT INTO ticket_activity (
                    ticket_id,
                    activity_type,
                    comment,
                    old_status,
                    new_status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    "CATEGORY_CHANGE",
                    "Ticket category updated",
                    None,
                    None
                )
            )

        changed_fields = ", ".join(updates.keys())

        cur.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                activity_type,
                comment
            )
            VALUES (%s, %s, %s)
            """,
            (
                ticket_id,
                "TICKET_UPDATED",
                f"Updated fields: {changed_fields}"
            )
        )

        # Record the operation in user activity.
        # Actor identification will be added with authentication.
        cur.execute(
            """
            INSERT INTO user_activity (
                activity_type,
                description,
                ticket_id
            )
            VALUES (%s, %s, %s)
            """,
            (
                "TICKET_UPDATED",
                f"Updated ticket #{ticket_id}: {changed_fields}",
                ticket_id
            )
        )

        return get_ticket_by_id(conn, ticket_id)



from psycopg import Connection


def get_ticket_history(conn: Connection, ticket_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                activity_id,
                ticket_id,
                performed_by,
                activity_type,
                comment,
                old_status,
                new_status,
                old_priority,
                new_priority,
                created_at
            FROM ticket_activity
            WHERE ticket_id = %s
            ORDER BY created_at ASC, activity_id ASC
            """,
            (ticket_id,)
        )

        return cur.fetchall()

def update_ticket_status(
    conn: Connection,
    ticket_id: int,
    new_status: str,
    updated_by: int
):
    with conn.cursor() as cur:

        # Lock the ticket row while processing the update
        cur.execute(
            """
            SELECT ticket_id, status
            FROM tickets
            WHERE ticket_id = %s
            FOR UPDATE
            """,
            (ticket_id,)
        )

        ticket = cur.fetchone()

        if ticket is None:
            return {"error": "TICKET_NOT_FOUND"}

        old_status = ticket["status"]

        # Check whether the new status is a valid transition
        allowed_transitions = {
            "OPEN": ["IN_PROGRESS"],
            "IN_PROGRESS": ["RESOLVED"],
            "RESOLVED": ["CLOSED"],
            "CLOSED": []
        }

        if new_status not in allowed_transitions[old_status]:
            return {
                "error": "INVALID_TRANSITION",
                "current_status": old_status,
                "requested_status": new_status
            }

        # Verify the user performing the update
        cur.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE user_id = %s
              AND is_active = TRUE
              AND role IN ('SUPPORT', 'ADMIN')
            """,
            (updated_by,)
        )

        actor = cur.fetchone()

        if actor is None:
            return {"error": "INVALID_ACTOR"}

        # If the actor is support staff, verify active assignment
        if actor["role"] == "SUPPORT":
            cur.execute(
                """
                SELECT ss.staff_id
                FROM support_staff ss
                WHERE ss.user_id = %s
                  AND EXISTS (
                      SELECT 1
                      FROM ticket_assignments ta
                      WHERE ta.ticket_id = %s
                        AND ta.staff_id = ss.staff_id
                        AND ta.assignment_status = 'ACTIVE'
                  )
                """,
                (updated_by, ticket_id)
            )

            if cur.fetchone() is None:
                return {"error": "NOT_ASSIGNED"}

        # Update ticket status
        cur.execute(
            """
            UPDATE tickets
            SET status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
            RETURNING *
            """,
            (new_status, ticket_id)
        )

        updated_ticket = cur.fetchone()

        # Record ticket activity
        cur.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                performed_by,
                activity_type,
                comment,
                old_status,
                new_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                ticket_id,
                updated_by,
                "STATUS_CHANGE",
                f"Status changed from {old_status} to {new_status}",
                old_status,
                new_status
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
                updated_by,
                "STATUS_UPDATED",
                f"Changed ticket #{ticket_id} from {old_status} to {new_status}",
                ticket_id
            )
        )

        return get_ticket_by_id(conn, ticket_id)

def update_ticket_priority(
    conn: Connection,
    ticket_id: int,
    new_priority: str,
    updated_by: int
):
    with conn.cursor() as cur:

        # Check ticket existence and lock its row
        cur.execute(
            """
            SELECT ticket_id, priority
            FROM tickets
            WHERE ticket_id = %s
            FOR UPDATE
            """,
            (ticket_id,)
        )

        ticket = cur.fetchone()

        if ticket is None:
            return {"error": "TICKET_NOT_FOUND"}

        old_priority = ticket["priority"]

        # Verify the user performing the update
        cur.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE user_id = %s
              AND is_active = TRUE
              AND role IN ('SUPPORT', 'ADMIN')
            """,
            (updated_by,)
        )

        actor = cur.fetchone()

        if actor is None:
            return {"error": "INVALID_ACTOR"}

        # Support staff must be actively assigned to this ticket
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
                (updated_by, ticket_id)
            )

            if cur.fetchone() is None:
                return {"error": "NOT_ASSIGNED"}

        # Avoid creating unnecessary activity records
        if old_priority == new_priority:
            return {"error": "SAME_PRIORITY"}

        # Update ticket priority
        cur.execute(
            """
            UPDATE tickets
            SET priority = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = %s
            RETURNING *
            """,
            (new_priority, ticket_id)
        )

        updated_ticket = cur.fetchone()

        # Record ticket activity
        cur.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                performed_by,
                activity_type,
                comment,
                old_priority,
                new_priority
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                ticket_id,
                updated_by,
                "PRIORITY_CHANGE",
                f"Priority changed from {old_priority} to {new_priority}",
                old_priority,
                new_priority
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
                updated_by,
                "PRIORITY_UPDATED",
                f"Changed ticket #{ticket_id} priority from {old_priority} to {new_priority}",
                ticket_id
            )
        )

        return get_ticket_by_id(conn, ticket_id)

def add_ticket_comment(
    conn: Connection,
    ticket_id: int,
    comment: str,
    added_by: int
):
    with conn.cursor() as cur:

        # Verify that the ticket exists
        cur.execute(
            """
            SELECT ticket_id, requester_id
            FROM tickets
            WHERE ticket_id = %s
            """,
            (ticket_id,)
        )

        ticket = cur.fetchone()

        if ticket is None:
            return {"error": "TICKET_NOT_FOUND"}

        # Verify the user is active
        cur.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE user_id = %s
              AND is_active = TRUE
            """,
            (added_by,)
        )

        actor = cur.fetchone()

        if actor is None:
            return {"error": "USER_NOT_FOUND"}

        # Employees can comment only on their own tickets
        if actor["role"] == "EMPLOYEE":
            if actor["user_id"] != ticket["requester_id"]:
                return {"error": "NOT_AUTHORIZED"}

        # Support staff can comment only on tickets assigned to them
        elif actor["role"] == "SUPPORT":
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
                (added_by, ticket_id)
            )

            if cur.fetchone() is None:
                return {"error": "NOT_ASSIGNED"}

        elif actor["role"] != "ADMIN":
            return {"error": "NOT_AUTHORIZED"}

        # Insert comment into ticket activity
        cur.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                performed_by,
                activity_type,
                comment
            )
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (
                ticket_id,
                added_by,
                "COMMENT",
                comment
            )
        )

        activity = cur.fetchone()

        # Record the action in user activity
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
                added_by,
                "COMMENT_ADDED",
                f"Added a comment to ticket #{ticket_id}",
                ticket_id
            )
        )

        return activity
