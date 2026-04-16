import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM posts")
db.execute("DELETE FROM comments")

user_count = 1000
post_count = 10**5
comment_count = 10**6

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)", ["user" + str(i)])

for i in range(1, post_count + 1):
    db.execute("INSERT INTO posts (title) VALUES (?)", ["post" + str(i)])

for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    post_id = random.randint(1, post_count)
    db.execute(
        """INSERT INTO comments (content, sent_at, user_id, post_id)
                  VALUES (?, datetime('now'), ?, ?)""",
        ["comment" + str(i), user_id, post_id],
    )

db.commit()
db.close()
