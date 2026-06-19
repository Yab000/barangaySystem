from db_config import get_db_connection

def add_history(username, service, purpose, status, appointment_date, queue_id=None):

    conn = get_db_connection()
    if not conn:
        print("DB ERROR: No connection available for history logging")
        return

    try:
        cur = conn.cursor()

        query = """
            INSERT INTO transaction_history
            (queue_id, username, action, details, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
        """

        details = f"{service} | {purpose} | {status} | {appointment_date}"

        cur.execute(query, (
            queue_id if queue_id else "N/A",
            username,
            status,
            details
        ))

        conn.commit()

    except Exception as e:
        print(f"ADD HISTORY ERROR: {e}")

    finally:
        if conn:
            conn.close()