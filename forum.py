import db


def get_posts():
    sql = """SELECT p.id, p.title, COUNT(c.id) total, MAX(c.sent_at) last
             FROM posts p
             LEFT JOIN comments c ON p.id = c.post_id
             GROUP BY p.id
             ORDER BY p.id DESC"""
    return db.query(sql)


def add_post(title, content, user_id):
    sql = "INSERT INTO posts (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    return db.last_insert_id()
