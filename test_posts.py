"""Posts feature check. Runs against a temporary database: python test_posts.py"""
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import seed_db
from app import MAX_POST_LENGTH, app

ROOT = Path(__file__).parent


def login(client, email="maya.chen@example.com", password=seed_db.SAMPLE_PASSWORD):
    return client.post("/login", data={"email": email, "password": password})


def main():
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, str(ROOT / "create_db.py")], cwd=tmp, check=True)
        db_path = Path(tmp) / "social.db"
        seed_conn = sqlite3.connect(db_path)
        seed_db.seed(seed_conn)
        seed_conn.close()
        app.config["DATABASE"] = db_path

        def scalar(sql, *args):
            conn = sqlite3.connect(db_path)
            try:
                return conn.execute(sql, args).fetchone()[0]
            finally:
                conn.close()

        client = app.test_client()

        # Login is required and checks the password.
        assert client.get("/").status_code == 302
        assert client.post("/posts", data={"content": "anon"}).status_code == 302
        assert scalar("SELECT COUNT(*) FROM Posts") == 15
        assert b"Incorrect" in login(client, password="wrong").data
        assert b"Incorrect" in login(client, email="nobody@example.com").data
        assert login(client).status_code == 302

        # Feed: own and accepted friends only. Nina (15) is pending, Sofia (5) is a stranger.
        page = client.get("/").get_data(as_text=True)
        assert "Sourdough attempt" in page and "half marathon" in page and "sci-fi" in page
        assert "pottery class" not in page and "Terracotta" not in page

        # User page shows anyone's posts.
        assert "Terracotta" in client.get("/users/5/posts").get_data(as_text=True)
        assert client.get("/users/999/posts").status_code == 404

        # Create: stored, escaped, and validated.
        client.post("/posts", data={"content": "  <script>x</script>  "})
        assert scalar("SELECT content FROM Posts WHERE postID = 16") == "<script>x</script>"
        assert scalar("SELECT userID FROM Posts WHERE postID = 16") == 1
        assert "<script>x</script>" not in client.get("/").get_data(as_text=True)
        client.post("/posts", data={"content": "   "})
        client.post("/posts", data={"content": "x" * (MAX_POST_LENGTH + 1)})
        assert scalar("SELECT COUNT(*) FROM Posts") == 16

        # Edit: owner only, and invalid edits change nothing.
        client.post("/posts/16/edit", data={"content": "Edited"})
        assert scalar("SELECT content FROM Posts WHERE postID = 16") == "Edited"
        client.post("/posts/16/edit", data={"content": " "})
        assert scalar("SELECT content FROM Posts WHERE postID = 16") == "Edited"
        assert client.get("/posts/4/edit").status_code == 403
        assert client.post("/posts/4/edit", data={"content": "hacked"}).status_code == 403
        assert client.post("/posts/999/edit", data={"content": "x"}).status_code == 404
        assert "sci-fi" in scalar("SELECT content FROM Posts WHERE postID = 4")

        # Delete: owner only, and child comments and likes go with the post.
        assert client.post("/posts/4/delete").status_code == 403
        assert scalar("SELECT COUNT(*) FROM Posts WHERE postID = 4") == 1
        assert scalar("SELECT COUNT(*) FROM Comments WHERE postID = 1") == 2
        assert scalar("SELECT COUNT(*) FROM Likes WHERE postID = 1") == 2
        assert client.post("/posts/1/delete").status_code == 302
        assert scalar("SELECT COUNT(*) FROM Posts WHERE postID = 1") == 0
        assert scalar("SELECT COUNT(*) FROM Comments WHERE postID = 1") == 0
        assert scalar("SELECT COUNT(*) FROM Likes WHERE postID = 1") == 0

        # Logout ends the session.
        client.post("/logout")
        assert client.get("/").status_code == 302

    print("All posts checks passed.")


if __name__ == "__main__":
    main()
