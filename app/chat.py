from .db import get_connection


def create_conversation(title):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO conversations(title) VALUES(?)",
        (title,)
    )

    conn.commit()

    conversation_id = cursor.lastrowid

    conn.close()

    return conversation_id


def add_message(conversation_id, role, content):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages
        (conversation_id, role, content)
        VALUES (?, ?, ?)
    """, (conversation_id, role, content))

    conn.commit()
    conn.close()


def get_messages(conversation_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM messages
        WHERE conversation_id=?
        ORDER BY id
    """, (conversation_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_conversations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM conversations
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def update_conversation_title(conversation_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE conversations
        SET title = ?
        WHERE id = ?
    """, (title, conversation_id))

    conn.commit()
    conn.close()

def rename_chat(self, conversation_id, title):
    update_conversation_title(conversation_id, title)

    # Refresh the chat list
    self.load_chat_history()