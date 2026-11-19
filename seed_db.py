"""Reset social.db to a known set of sample data (15 rows per table).

Safe to re-run: every run REPLACES all existing rows, in one transaction.
If anything fails, the database is left exactly as it was.
"""
import hashlib
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("social.db")

# Shared login for every sample account. Development data only.
SAMPLE_PASSWORD = "SamplePass123!"
HASH_ITERATIONS = 600_000


def hash_password(password, salt):
    """Same format as werkzeug.security, so check_password_hash() can verify it."""
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), HASH_ITERATIONS
    ).hex()
    return f"pbkdf2:sha256:{HASH_ITERATIONS}${salt}${digest}"


# IDs are assigned 1-15 in list order, and the tables below refer to them.
USERS = [
    ("maya_chen", "maya.chen@example.com", "Home cook and weekend photographer.", "2026-01-05"),
    ("jordan_reyes", "jordan.reyes@example.com", "Sci-fi reader. Coffee enthusiast.", "2026-01-08"),
    ("priya_nair", "priya.nair@example.com", "Distance runner and data analyst.", "2026-01-12"),
    ("liam_oconnor", "liam.oconnor@example.com", "Dog person. High school history teacher.", "2026-01-15"),
    ("sofia_martinez", "sofia.martinez@example.com", "Interior design student who loves color.", "2026-01-20"),
    ("noah_kim", "noah.kim@example.com", "Woodworking on weekends, software on weekdays.", "2026-01-24"),
    ("amara_okafor", "amara.okafor@example.com", "Always planning the next hike.", "2026-02-01"),
    ("caleb_brooks", "caleb.brooks@example.com", "Guitarist looking for a band.", "2026-02-06"),
    ("hana_tanaka", "hana.tanaka@example.com", "Botany major. Happiest outdoors.", "2026-02-11"),
    ("diego_santos", "diego.santos@example.com", "Junior developer and Sunday soccer player.", "2026-02-17"),
    ("zoe_williams", "zoe.williams@example.com", "Film buff with strong opinions on popcorn.", "2026-02-22"),
    ("omar_haddad", "omar.haddad@example.com", "New in town and looking for a soccer team.", "2026-03-01"),
    ("grace_lee", "grace.lee@example.com", "Nursing graduate. Powered by iced tea.", "2026-03-07"),
    ("mateo_rivera", "mateo.rivera@example.com", "Road trips, playlists, and gas station snacks.", "2026-03-14"),
    ("nina_petrova", "nina.petrova@example.com", "Beginner potter and lifelong art lover.", "2026-03-20"),
]

# (userID, content, postDate)
POSTS = [
    (1, "Finally tried the new ramen spot on 5th Street. The spicy miso is worth the wait.", "2026-04-02"),
    (3, "Finished my first half marathon this morning! My legs are gone, but I am so happy.", "2026-04-05"),
    (5, "Repainted the living room over the weekend. Terracotta was the right call.", "2026-04-09"),
    (2, "Anyone have good sci-fi recommendations? I just ran out of books.", "2026-04-14"),
    (7, "Sunrise hike at the reservoir today. Completely worth the 5 a.m. alarm.", "2026-04-20"),
    (10, "Got my first open source pull request merged today. Small fix, big smile.", "2026-04-26"),
    (1, "Sourdough attempt number four actually rose. Sharing slices with the neighbors.", "2026-05-03"),
    (9, "The cherry blossoms are nearly gone, so I took one last walk through the park.", "2026-05-10"),
    (12, "Looking for a pickup soccer group that plays on weekends. Any leads?", "2026-05-18"),
    (4, "Adopted this goofy rescue pup today. Everyone, meet Biscuit!", "2026-05-25"),
    (14, "My road trip playlist needs help. Drop your best driving songs.", "2026-06-02"),
    (6, "Built a standing desk from reclaimed wood. Only one extra trip to the hardware store.", "2026-06-11"),
    (13, "Passed my nursing boards! Thank you to everyone who quizzed me.", "2026-06-20"),
    (3, "Training for the fall marathon starts Monday. Wish me luck.", "2026-07-01"),
    (15, "First pottery class today. My bowl is more of a plate, but I love it.", "2026-07-12"),
]

# (postID, userID, content, commentDate)
COMMENTS = [
    (1, 2, "Saving this for Friday. Do they take reservations?", "2026-04-02 19:14:00"),
    (1, 1, "No reservations, so get there early. The line grows fast.", "2026-04-02 19:42:00"),
    (2, 1, "Huge congratulations! What was your finish time?", "2026-04-05 12:08:00"),
    (3, 7, "That color looks so warm. Can you send me the paint name?", "2026-04-09 20:31:00"),
    (4, 4, "Try The Martian if you want something fast and funny.", "2026-04-14 17:25:00"),
    (4, 6, "Seconded, and add The Left Hand of Darkness to your list.", "2026-04-15 08:47:00"),
    (5, 9, "Beautiful! Which trail did you take up there?", "2026-04-20 10:16:00"),
    (6, 12, "Congrats! The first merge always feels the best.", "2026-04-26 21:03:00"),
    (7, 3, "Number four looks perfect. Please save me a slice.", "2026-05-03 15:22:00"),
    (8, 10, "Great timing. They will be gone by next week.", "2026-05-10 18:55:00"),
    (9, 10, "We play Sundays at Riverside Field. You should join us!", "2026-05-18 13:37:00"),
    (10, 2, "Biscuit is adorable. I need to meet this dog immediately.", "2026-05-25 16:49:00"),
    (11, 13, "You cannot do a road trip without some classic Fleetwood Mac.", "2026-06-02 22:11:00"),
    (13, 14, "So proud of you, Grace. Celebration dinner is on me!", "2026-06-20 19:28:00"),
    (15, 1, "A plate is still a win. I would happily eat off of it.", "2026-07-13 09:34:00"),
]

# (postID, userID, LikeDate). A user likes a post at most once, never their own.
LIKES = [
    (1, 3, "2026-04-02 20:05:00"),
    (1, 2, "2026-04-02 19:15:00"),
    (2, 1, "2026-04-05 12:07:00"),
    (2, 5, "2026-04-05 14:30:00"),
    (3, 7, "2026-04-09 20:30:00"),
    (4, 1, "2026-04-14 18:02:00"),
    (5, 9, "2026-04-20 10:15:00"),
    (6, 12, "2026-04-26 21:02:00"),
    (7, 2, "2026-05-03 17:44:00"),
    (8, 7, "2026-05-10 19:20:00"),
    (10, 6, "2026-05-25 18:09:00"),
    (10, 2, "2026-05-25 16:48:00"),
    (13, 11, "2026-06-20 20:13:00"),
    (14, 5, "2026-07-01 11:26:00"),
    (15, 13, "2026-07-12 21:40:00"),
]

# (userID1, userID2, status, friendshipDate). status: 1 = accepted, 0 = pending.
# userID1 sent the request. The chains leave mutual friends for suggestions.
FRIENDSHIPS = [
    (1, 2, 1, "2026-03-22"),
    (1, 3, 1, "2026-03-23"),
    (2, 4, 1, "2026-03-25"),
    (3, 5, 1, "2026-03-26"),
    (4, 6, 1, "2026-03-28"),
    (5, 7, 1, "2026-03-30"),
    (6, 8, 1, "2026-04-01"),
    (7, 9, 1, "2026-04-03"),
    (9, 10, 1, "2026-04-06"),
    (10, 12, 1, "2026-04-08"),
    (11, 13, 1, "2026-04-12"),
    (13, 14, 1, "2026-04-15"),
    (15, 1, 0, "2026-07-15"),
    (8, 11, 0, "2026-07-20"),
    (14, 12, 0, "2026-08-02"),
]

# (senderID, reciverID, messageContent, sentDate). Only accepted friends message.
MESSAGES = [
    (1, 2, "Ramen on Friday? I can get there by six.", "2026-08-03"),
    (2, 1, "Yes! I will meet you outside.", "2026-08-03"),
    (1, 2, "Perfect. Bring your appetite.", "2026-08-04"),
    (3, 5, "Your living room looks amazing. Any tips for picking colors?", "2026-08-09"),
    (5, 3, "Always test a sample on the wall first. Happy to help you choose.", "2026-08-10"),
    (3, 5, "Thank you! I will pick up some samples this weekend.", "2026-08-10"),
    (7, 9, "Want to hike the reservoir trail next Saturday?", "2026-08-16"),
    (9, 7, "Count me in. I will bring snacks.", "2026-08-17"),
    (9, 10, "Do you know any good plant shops near campus?", "2026-08-24"),
    (10, 9, "There is a great one next to the library.", "2026-08-24"),
    (13, 14, "Are you still leaving for your road trip on Thursday?", "2026-09-02"),
    (14, 13, "Yes, and the playlist is finally done.", "2026-09-02"),
    (13, 14, "Drive safe, and send pictures!", "2026-09-03"),
    (4, 6, "Biscuit chewed through another leash. Could you build me a dog gate?", "2026-09-14"),
    (6, 4, "Absolutely. Send me the measurements.", "2026-09-15"),
]

# Children first on delete; parents first on insert.
TABLES = ["Messages", "Friendships", "Likes", "Comments", "Posts", "Users"]


def seed(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    with conn:  # Commits on success, rolls everything back on any error.
        for table in TABLES:
            conn.execute(f"DELETE FROM {table}")
        # Restart AUTOINCREMENT so the IDs above stay correct on every run.
        conn.execute("DELETE FROM sqlite_sequence")

        conn.executemany(
            "INSERT INTO Users (username, email, password, bio, joinDate) VALUES (?, ?, ?, ?, ?)",
            [
                (name, email, hash_password(SAMPLE_PASSWORD, name), bio, joined)
                for name, email, bio, joined in USERS
            ],
        )
        conn.executemany("INSERT INTO Posts (userID, content, postDate) VALUES (?, ?, ?)", POSTS)
        conn.executemany(
            "INSERT INTO Comments (postID, userID, content, commentDate) VALUES (?, ?, ?, ?)",
            COMMENTS,
        )
        conn.executemany("INSERT INTO Likes (postID, userID, LikeDate) VALUES (?, ?, ?)", LIKES)
        conn.executemany(
            "INSERT INTO Friendships (userID1, userID2, status, friendshipDate) VALUES (?, ?, ?, ?)",
            FRIENDSHIPS,
        )
        conn.executemany(
            "INSERT INTO Messages (senderID, reciverID, messageContent, sentDate) VALUES (?, ?, ?, ?)",
            MESSAGES,
        )

        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in reversed(TABLES)
        }
        assert all(count == 15 for count in counts.values()), counts
    return counts


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    try:
        for table, count in seed(conn).items():
            print(f"{table}: {count}")
    finally:
        conn.close()
