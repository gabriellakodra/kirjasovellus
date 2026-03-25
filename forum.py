import db


def get_posts():
    sql = """SELECT p.id, p.title, COUNT(c.id) total, MAX(c.sent_at) last
             FROM posts p
             LEFT JOIN comments c ON p.id = c.post_id
             GROUP BY p.id
             ORDER BY p.id DESC"""
    return db.query(sql)


def get_post(post_id):
    sql = "SELECT id, title FROM posts WHERE id = ?"
    return db.query(sql, [post_id])[0]


def get_comments(post_id):
    sql = """SELECT c.id, c.content, c.sent_at, c.user_id, u.username
             FROM comments c, users u
             WHERE c.user_id = u.id AND c.post_id = ?
             ORDER BY c.id"""
    return db.query(sql, [post_id])


def add_post(title, content, user_id):
    sql = "INSERT INTO posts (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    return db.last_insert_id()


def add_comment(content, post_id, user_id):
    sql = "INSERT INTO comments (content, post_id, user_id, sent_at) VALUES (?, ?, ?, datetime('now'))"
    db.execute(sql, [content, post_id, user_id])
