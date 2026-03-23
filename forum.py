import db


def get_posts():
    sql = """SELECT p.id, p.title, COUNT(c.id) total, MAX(c.sent_at) last
             FROM posts p, comments c
             WHERE p.id = c.thread_id
             GROUP BY p.id
             ORDER BY p.id DESC"""
    return db.query(sql)
