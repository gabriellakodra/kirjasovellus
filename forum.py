import db
import sqlite3


def get_posts():
    sql = """SELECT p.id, p.title, COUNT(c.id) total, MAX(c.sent_at) last
             FROM posts p
             LEFT JOIN comments c ON p.id = c.post_id
             GROUP BY p.id
             ORDER BY p.id DESC"""
    return db.query(sql)


def get_post(post_id):
    sql = "SELECT id, title, content, user_id FROM posts WHERE id = ?"
    result = db.query(sql, [post_id])
    return result[0] if result else None


def get_comments(post_id):
    sql = """SELECT c.id, c.content, c.sent_at, c.user_id, u.username, u.id user_id
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
    try:
        db.execute(sql, [content, user_id, post_id])
        return None
    except sqlite3.IntegrityError:
        return "VIRHE: kommentin lisääminen epäonnistui"


def update_comment(comment_id, content):
    sql = "UPDATE comments SET content = ? WHERE id = ?"
    db.execute(sql, [content, comment_id])


def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])


def update_post(post_id, title, content):
    sql = "UPDATE posts SET title = ?, content = ? WHERE id = ?"
    db.execute(sql, [title, content, post_id])


def remove_post(post_id):
    sql = "DELETE FROM post_classes WHERE post_id = ?"
    db.execute(sql, [post_id])
    sql = "DELETE FROM comments WHERE post_id = ?"
    db.execute(sql, [post_id])
    sql = "DELETE FROM posts WHERE id = ?"
    db.execute(sql, [post_id])


def search(query):
    sql = """
    SELECT c.id comment_id,
           c.post_id,
           p.title post_title,
           c.sent_at,
           u.username,
           u.id user_id,
           'comment' as type
    FROM posts p, comments c, users u
    WHERE p.id = c.post_id AND
          u.id = c.user_id AND
          c.content LIKE ?
    
    UNION
    
    SELECT NULL comment_id,
           p.id post_id,
           p.title post_title,
           NULL sent_at,
           u.username,
           u.id user_id,
           'post' as type
    FROM posts p, users u
    WHERE p.user_id = u.id AND
          (p.title LIKE ? OR p.content LIKE ?)
    
    UNION
    
    SELECT NULL comment_id,
           NULL post_id,
           u.username post_title,
           NULL sent_at,
           u.username,
           u.id user_id,
           'user' as type
    FROM users u
    WHERE u.username LIKE ?
    
    ORDER BY post_id DESC, user_id DESC
    """
    return db.query(
        sql,
        ["%" + query + "%", "%" + query + "%", "%" + query + "%", "%" + query + "%"],
    )


def create_user(username, password_hash):
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    try:
        db.execute(sql, [username, password_hash])
        return None
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"


def get_user(username):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes


def get_classes(post_id):
    sql = "SELECT title, value FROM post_classes WHERE post_id = ?"
    return db.query(sql, [post_id])


def add_post_classes(post_id, classes_dict):
    """Save selected classes for a post"""
    for title, value in classes_dict.items():
        if value:
            sql = "INSERT INTO post_classes (post_id, title, value) VALUES (?, ?, ?)"
            db.execute(sql, [post_id, title, value])


def update_post_classes(post_id, classes_dict):
    """Update classes for a post"""
    sql = "DELETE FROM post_classes WHERE post_id = ?"
    db.execute(sql, [post_id])
    add_post_classes(post_id, classes_dict)
