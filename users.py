import db


def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_posts(user_id):
    sql = """SELECT p.id, p.title, COUNT(c.id) total
             FROM posts p
             LEFT JOIN comments c ON p.id = c.post_id
             WHERE p.user_id = ?
             GROUP BY p.id
             ORDER BY p.id DESC"""
    return db.query(sql, [user_id])


def get_comments(user_id):
    sql = """SELECT c.id,
                    c.post_id,
                    p.title post_title,
                    c.sent_at
             FROM posts p, comments c
             WHERE p.id = c.post_id AND
                   c.user_id = ?
             ORDER BY c.sent_at DESC"""
    return db.query(sql, [user_id])
