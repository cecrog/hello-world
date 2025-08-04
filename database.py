import sqlite3
import json
from datetime import datetime
from config import DB_PATH

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create articles table for RSS feeds
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            link TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            published_date TEXT,
            content TEXT,
            sentiment_score REAL,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create tweets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT,
            retweet_count INTEGER,
            like_count INTEGER,
            sentiment_score REAL,
            keywords TEXT,
            stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create keywords table for tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keyword_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            alert_enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def store_article(article_data):
    """Store an RSS article in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO articles 
            (title, description, link, source, published_date, content, sentiment_score, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data['title'],
            article_data['description'],
            article_data['link'],
            article_data['source'],
            article_data['published_date'],
            article_data['content'],
            article_data.get('sentiment_score'),
            json.dumps(article_data.get('keywords', []))
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing article: {e}")
        return False
    finally:
        conn.close()

def store_tweet(tweet_data):
    """Store a tweet in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO tweets 
            (tweet_id, username, content, created_at, retweet_count, like_count, sentiment_score, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tweet_data['tweet_id'],
            tweet_data['username'],
            tweet_data['content'],
            tweet_data['created_at'],
            tweet_data.get('retweet_count', 0),
            tweet_data.get('like_count', 0),
            tweet_data.get('sentiment_score'),
            json.dumps(tweet_data.get('keywords', []))
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing tweet: {e}")
        return False
    finally:
        conn.close()

def get_recent_articles(limit=50, source=None):
    """Retrieve recent articles from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT title, description, link, source, published_date, sentiment_score, keywords, created_at
        FROM articles
    '''
    params = []
    
    if source:
        query += ' WHERE source = ?'
        params.append(source)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'title': row[0],
            'description': row[1],
            'link': row[2],
            'source': row[3],
            'published_date': row[4],
            'sentiment_score': row[5],
            'keywords': json.loads(row[6]) if row[6] else [],
            'created_at': row[7]
        }
        for row in results
    ]

def get_recent_tweets(limit=50, username=None):
    """Retrieve recent tweets from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT tweet_id, username, content, created_at, retweet_count, like_count, sentiment_score, keywords, stored_at
        FROM tweets
    '''
    params = []
    
    if username:
        query += ' WHERE username = ?'
        params.append(username)
    
    query += ' ORDER BY stored_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'tweet_id': row[0],
            'username': row[1],
            'content': row[2],
            'created_at': row[3],
            'retweet_count': row[4],
            'like_count': row[5],
            'sentiment_score': row[6],
            'keywords': json.loads(row[7]) if row[7] else [],
            'stored_at': row[8]
        }
        for row in results
    ]

def search_content(query, content_type='all'):
    """Search for content by keyword."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    results = []
    
    if content_type in ['all', 'articles']:
        cursor.execute('''
            SELECT title, description, link, source, published_date, sentiment_score, created_at, 'article' as type
            FROM articles
            WHERE title LIKE ? OR description LIKE ? OR keywords LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        results.extend(cursor.fetchall())
    
    if content_type in ['all', 'tweets']:
        cursor.execute('''
            SELECT tweet_id, username, content, created_at, sentiment_score, stored_at, 'tweet' as type, ''
            FROM tweets
            WHERE content LIKE ? OR keywords LIKE ?
            ORDER BY stored_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        results.extend(cursor.fetchall())
    
    conn.close()
    return results