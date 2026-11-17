
def get_recent_tickets(conn, exclude_ticket_id: int, limit: int = 20):

    query = """
        SELECT
            ticket_id,
            title,
            description,
            category,
            priority,
            status
        FROM tickets
        WHERE ticket_id != %s
        ORDER BY created_at DESC, ticket_id DESC
        LIMIT %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (exclude_ticket_id, limit)
        )

        return cursor.fetchall()


def save_ai_suggestion(conn, ticket_id: int, suggestion: dict, model_name: str):

    query = """
        INSERT INTO ai_suggestions
        (
            ticket_id,
            suggested_category,
            suggested_priority,
            troubleshooting_steps,
            explanation,
            model_name
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING suggestion_id, created_at;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (
                ticket_id,
                suggestion["suggested_category"],
                suggestion["suggested_priority"],
                suggestion["troubleshooting_steps"],
                suggestion["explanation"],
                model_name
            )
        )

        return cursor.fetchone()



def save_ai_feedback(
    conn,
    suggestion_id: int,
    feedback: dict,
    final_category: str | None,
    final_priority: str | None
):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT t.ticket_id, t.category, t.priority
            FROM ai_suggestions s
            JOIN tickets t ON t.ticket_id = s.ticket_id
            WHERE s.suggestion_id = %s
            FOR UPDATE OF t;
            """,
            (suggestion_id,)
        )
        ticket = cursor.fetchone()

        if ticket is None:
            raise LookupError(
                f"Ticket for AI suggestion {suggestion_id} no longer exists"
            )

        cursor.execute(
            """
            INSERT INTO ai_feedback
            (
                suggestion_id,
                reviewed_by,
                is_useful,
                decision,
                corrected_category,
                corrected_priority,
                final_category,
                final_priority,
                comments
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
                feedback_id,
                suggestion_id,
                reviewed_by,
                is_useful,
                decision,
                corrected_category,
                corrected_priority,
                final_category,
                final_priority,
                comments;
            """,
            (
                suggestion_id,
                feedback["reviewed_by"],
                feedback["is_useful"],
                feedback["decision"],
                feedback.get("corrected_category"),
                feedback.get("corrected_priority"),
                final_category,
                final_priority,
                feedback.get("comments")
            )
        )

        saved_feedback = cursor.fetchone()

        if final_category is not None or final_priority is not None:
            cursor.execute(
                """
                UPDATE tickets
                SET category = COALESCE(%s, category),
                    priority = COALESCE(%s, priority),
                    updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = %s;
                """,
                (final_category, final_priority, ticket["ticket_id"])
            )

        if feedback["decision"] == "REJECTED":
            activity_comment = (
                f"AI suggestion #{suggestion_id} was rejected; "
                "ticket category and priority were not changed."
            )
        else:
            activity_comment = (
                f"AI suggestion #{suggestion_id} was "
                f"{feedback['decision'].lower()}; human-confirmed category "
                f"{final_category} and priority {final_priority}."
            )

        cursor.execute(
            """
            INSERT INTO ticket_activity (
                ticket_id,
                performed_by,
                activity_type,
                comment,
                old_priority,
                new_priority
            )
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                ticket["ticket_id"],
                feedback["reviewed_by"],
                "AI_FEEDBACK_REVIEWED",
                activity_comment,
                ticket["priority"],
                final_priority if final_priority is not None else ticket["priority"]
            )
        )

        cursor.execute(
            """
            INSERT INTO user_activity (
                user_id,
                activity_type,
                description,
                ticket_id
            )
            VALUES (%s, %s, %s, %s);
            """,
            (
                feedback["reviewed_by"],
                "AI_FEEDBACK_SUBMITTED",
                f"Reviewed AI suggestion #{suggestion_id}",
                ticket["ticket_id"]
            )
        )

        return saved_feedback



def get_ai_suggestion_by_id(conn, suggestion_id: int):

    query = """
        SELECT
            suggestion_id,
            ticket_id,
            suggested_category,
            suggested_priority
        FROM ai_suggestions
        WHERE suggestion_id = %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (suggestion_id,))
        return cursor.fetchone()


def get_active_support_staff(conn, staff_id: int):

    query = """
        SELECT ss.staff_id
        FROM support_staff ss
        JOIN users u
            ON ss.user_id = u.user_id
        WHERE ss.staff_id = %s
          AND u.role = 'SUPPORT'
          AND u.is_active = TRUE;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (staff_id,))
        return cursor.fetchone()



def get_ai_suggestions_by_ticket(conn, ticket_id: int):

    query = """
        SELECT
            suggestion_id,
            ticket_id,
            suggested_category,
            suggested_priority,
            troubleshooting_steps,
            explanation,
            model_name,
            created_at
        FROM ai_suggestions
        WHERE ticket_id = %s
        ORDER BY created_at DESC, suggestion_id DESC;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (ticket_id,))
        return cursor.fetchall()


def get_feedback_by_suggestion_ids(conn, suggestion_ids: list[int]):

    if not suggestion_ids:
        return []

    query = """
        SELECT
            feedback_id,
            suggestion_id,
            reviewed_by,
            is_useful,
            corrected_category,
            corrected_priority,
            final_category,
            final_priority,
            comments
        FROM ai_feedback
        WHERE suggestion_id = ANY(%s)
        ORDER BY feedback_id DESC;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (suggestion_ids,))
        return cursor.fetchall()
