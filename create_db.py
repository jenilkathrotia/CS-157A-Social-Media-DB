import sqlite3

create_query = """
    DROP TABLE IF EXISTS Users;
    DROP TABLE IF EXISTS Posts;
    DROP TABLE IF EXISTS Comments;
    DROP TABLE IF EXISTS Likes;
    DROP TABLE IF EXISTS Friendships;
    DROP TABLE IF EXISTS Messages;
    CREATE TABLE Users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        bio TEXT,
        joinDate DATE
    );
    CREATE TABLE Posts (
        postID INTEGER PRIMARY KEY AUTOINCREMENT,
        userID INTEGER NOT NULL,
        content BLOB NOT NULL,
        postDate DATE,
        FOREIGN KEY (userID) REFERENCES Users (userID)
    );
    CREATE TABLE Comments (
        commentID INTEGER PRIMARY KEY AUTOINCREMENT,
        postID INTEGER NOT NULL,
        userID INTEGER NOT NULL,
        content TEXT NOT NULL,
        commentDate DATETIME,
        FOREIGN KEY (postID) REFERENCES Posts (postID),
        FOREIGN KEY (userID) REFERENCES Users (userID)
    );
    CREATE TABLE Likes (
        postID INTEGER,
        userID INTEGER,
        LikeDate DATETIME,
        PRIMARY KEY (postID, userID),
        FOREIGN KEY (postID) REFERENCES Posts (postID),
        FOREIGN KEY (userID) REFERENCES Users (userID)
    );
    CREATE TABLE Friendships (
        userID1 INTEGER,
        userID2 INTEGER,
        status BOOLEAN,
        friendshipDate DATE,
        FOREIGN KEY(userID1) REFERENCES Users(userID),
        FOREIGN KEY(userID2) REFERENCES Users(userID)
    );
    CREATE TABLE Messages (
        messageID INTEGER PRIMARY KEY AUTOINCREMENT,
        senderID INTEGER,
        reciverID INTEGER,
        messageContent BLOB NOT NULL,
        sentDate DATE,
        FOREIGN KEY(senderID) REFERENCES Users(userID),
        FOREIGN KEY(reciverID) REFERENCES Users(userID)
    );"""

with sqlite3.connect("social.db") as conn:
    cursor = conn.cursor()
    
    cursor.executescript(create_query)

