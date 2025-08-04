#!/usr/bin/env python3
"""
Fintech & Crypto News Collector

This script collects data from RSS feeds and Twitter, then stores it in the database.
Can be run manually or scheduled as a cron job.
"""

import sys
import time
from datetime import datetime

from database import init_database
from rss_aggregator import fetch_rss_feeds
from twitter_client import TwitterClient, test_twitter_connection

def main():
    """Main data collection function."""
    print("=" * 60)
    print("🚀 Fintech & Crypto News Collector")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize database
    print("🗄️  Initializing database...")
    init_database()
    print("✅ Database ready")
    
    total_new_articles = 0
    total_new_tweets = 0
    
    # Collect RSS feeds
    try:
        print("\n📰 Starting RSS feed collection...")
        total_new_articles = fetch_rss_feeds()
        print(f"✅ RSS collection completed: {total_new_articles} new articles")
    except Exception as e:
        print(f"❌ RSS collection failed: {e}")
    
    # Collect Twitter data
    try:
        print("\n🐦 Starting Twitter data collection...")
        
        # Test Twitter connection first
        if test_twitter_connection():
            twitter_client = TwitterClient()
            total_new_tweets = twitter_client.collect_all_tweets()
            print(f"✅ Twitter collection completed: {total_new_tweets} new tweets")
        else:
            print("⚠️  Twitter API not configured, skipping tweet collection")
            print("   To enable Twitter integration:")
            print("   1. Get API credentials from https://developer.twitter.com/")
            print("   2. Copy .env.example to .env and add your credentials")
    except Exception as e:
        print(f"❌ Twitter collection failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COLLECTION SUMMARY")
    print("=" * 60)
    print(f"📰 Articles collected: {total_new_articles}")
    print(f"🐦 Tweets collected: {total_new_tweets}")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return total_new_articles + total_new_tweets

if __name__ == "__main__":
    try:
        total_collected = main()
        sys.exit(0 if total_collected >= 0 else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)