import asyncio
import argparse
import sqlite3
import random
import time
import pandas as pd
from datetime import datetime
import asyncpraw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

REDDIT_CLIENT_ID = "YOUR_CLIENT_ID"
REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDDIT_USER_AGENT = "QuantOracle/1.0"

def init_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            score INTEGER,
            sentiment REAL,
            chain_signal TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON posts(sentiment);")
    conn.commit()
    conn.close()

def save_to_database(db_path, posts):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.executemany('''
            INSERT OR IGNORE INTO posts (id, subreddit, title, score, sentiment, chain_signal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', posts)
        conn.commit()
        print(f"Saved {len(posts)} posts to database")
    except Exception as err:
        print(f"Database error: {err}")
    finally:
        conn.close()

def setup_sentiment_analyzer():
    analyzer = SentimentIntensityAnalyzer()
    crypto_words = {
        'moon': 2.0,
        'rigged': -1.5,
        'scam': -2.0,
        'gem': 1.5,
        'rug': -3.0,
        'bullish': 1.0,
        'bearish': -1.0,
        'fud': -1.0,
        'hodl': 0.8,
        'airdrop': 0.5
    }
    analyzer.lexicon.update(crypto_words)
    return analyzer

def get_sentiment_score(analyzer, text):
    scores = analyzer.polarity_scores(text)
    return scores['compound']

def simulate_chain_activity():
    options = ['LOW_GAS', 'NORMAL', 'WHALE_ALERT']
    weights = [0.4, 0.5, 0.1]
    return random.choices(options, weights=weights)[0]

async def fetch_posts(reddit, subreddit_name, limit):
    posts = []
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        print(f"Fetching r/{subreddit_name}...")
        
        async for post in subreddit.hot(limit=limit):
            posts.append({
                'id': post.id,
                'subreddit': subreddit_name,
                'title': post.title,
                'score': post.score
            })
    except Exception as err:
        print(f"Error fetching r/{subreddit_name}: {err}")
    
    return posts

async def run_scraper(subreddits, limit, enable_sentiment, enable_chain):
    reddit = asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    analyzer = setup_sentiment_analyzer() if enable_sentiment else None
    
    all_posts = []
    for sub in subreddits:
        posts = await fetch_posts(reddit, sub, limit)
        all_posts.extend(posts)
    
    await reddit.close()
    
    results = []
    for post in all_posts:
        sentiment = 0.0
        if analyzer:
            sentiment = get_sentiment_score(analyzer, post['title'])
        
        chain_signal = "N/A"
        if enable_chain:
            chain_signal = simulate_chain_activity()
            time.sleep(random.uniform(0.05, 0.15))
        
        results.append((
            post['id'],
            post['subreddit'],
            post['title'],
            post['score'],
            sentiment,
            chain_signal
        ))
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Quant Oracle Backend")
    parser.add_argument('--subs', type=str, default='quant,ethereum,python')
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--sentiment', action='store_true')
    parser.add_argument('--chain', action='store_true')
    args = parser.parse_args()
    
    db_path = "oracle_data.db"
    init_database(db_path)
    
    subreddits = args.subs.split(',')
    print(f"Starting scraper for: {subreddits}")
    
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(
        run_scraper(subreddits, args.limit, args.sentiment, args.chain)
    )
    
    if results:
        save_to_database(db_path, results)
        
        df = pd.DataFrame(results, columns=[
            'id', 'subreddit', 'title', 'score', 'sentiment', 'chain_signal'
        ])
        df.to_csv('oracle_feed.csv', index=False)
        print(f"Exported {len(df)} rows to oracle_feed.csv")
    else:
        print("No data collected")

if __name__ == "__main__":
    main()
