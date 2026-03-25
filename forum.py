import db


def get_posts():
    sql = """SELECT p.id, p.title, COUNT(c.id) total, MAX(c.sent_at) last
             FROM posts p
             LEFT JOIN comments c ON p.id = c.post_id
             GROUP BY p.id
             ORDER BY p.id DESC"""
    return db.query(sql)


def get_post(post_id):
    sql = "SELECT id, title, content FROM posts WHERE id = ?"
    return db.query(sql, [post_id])[0]


def get_comments(post_id):
    sql = """SELECT c.id, c.content, c.sent_at, c.user_id, u.username
             FROM comments c, users u
             WHERE c.user_id = u.id AND c.post_id = ?
             ORDER BY c.id"""
    return db.query(sql, [post_id])


def get_comment(comment_id):
    sql = """SELECT c.id, c.content, c.post_id, c.user_id
             FROM comments c
             WHERE c.id = ?"""
    return db.query(sql, [comment_id])[0]


def add_post(title, content, user_id):
    sql = "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, content, user_id])
    return db.last_insert_id()


def add_comment(content, user_id, post_id):
    sql = """INSERT INTO comments (content, sent_at, user_id, post_id) VALUES
             (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, post_id])


def update_comment(comment_id, content):
    sql = "UPDATE comments SET content = ? WHERE id = ?"
    db.execute(sql, [content, comment_id])
