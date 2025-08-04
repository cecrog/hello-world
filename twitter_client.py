import tweepy
import time
from datetime import datetime, timedelta
from textblob import TextBlob
import re

from config import (
    TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_ACCOUNTS, FINTECH_KEYWORDS
)
from database import store_tweet, init_database
from rss_aggregator import extract_keywords, analyze_sentiment

class TwitterClient:
    def __init__(self):
        """Initialize Twitter API client."""
        self.client = None
        self.api = None
        self.setup_api()
    
    def setup_api(self):
        """Set up Twitter API authentication."""
        try:
            # Twitter API v2 client (for newer endpoints)
            if TWITTER_BEARER_TOKEN:
                self.client = tweepy.Client(
                    bearer_token=TWITTER_BEARER_TOKEN,
                    consumer_key=TWITTER_API_KEY,
                    consumer_secret=TWITTER_API_SECRET,
                    access_token=TWITTER_ACCESS_TOKEN,
                    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                    wait_on_rate_limit=True
                )
            
            # Twitter API v1.1 (for some legacy endpoints)
            if all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
                auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
                auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            print("✓ Twitter API client initialized")
            
        except Exception as e:
            print(f"✗ Error setting up Twitter API: {e}")
            print("Note: Twitter API credentials are required for tweet collection")
    
    def is_configured(self):
        """Check if Twitter API is properly configured."""
        return self.client is not None or self.api is not None
    
    def clean_tweet_text(self, text):
        """Clean tweet text by removing URLs, mentions, etc."""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def fetch_user_tweets(self, username, count=50):
        """Fetch recent tweets from a specific user."""
        if not self.client:
            return []
        
        try:
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"User {username} not found")
                return []
            
            user_id = user.data.id
            
            # Fetch tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(count, 100),
                tweet_fields=['created_at', 'public_metrics', 'context_annotations'],
                exclude=['retweets', 'replies']
            )
            
            processed_tweets = []
            
            if tweets.data:
                for tweet in tweets.data:
                    tweet_text = self.clean_tweet_text(tweet.text)
                    keywords = extract_keywords(tweet_text)
                    
                    # Only store if relevant to fintech/crypto
                    if keywords:
                        tweet_data = {
                            'tweet_id': str(tweet.id),
                            'username': username,
                            'content': tweet_text,
                            'created_at': tweet.created_at.isoformat() if tweet.created_at else '',
                            'retweet_count': tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            'like_count': tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            'sentiment_score': analyze_sentiment(tweet_text),
                            'keywords': keywords
                        }
                        
                        processed_tweets.append(tweet_data)
            
            return processed_tweets
            
        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")
            return []
    
    def fetch_keyword_tweets(self, keywords, count=100):
        """Fetch tweets containing specific keywords."""
        if not self.client:
            return []
        
        try:
            # Create search query
            query = " OR ".join([f'"{keyword}"' for keyword in keywords[:10]])  # Limit to avoid query length issues
            query += " -is:retweet lang:en"  # Exclude retweets, English only
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(count, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                user_fields=['username'],
                expansions=['author_id']
            )
            
            processed_tweets = []
            
            if tweets.data:
                # Create user lookup
                users = {}
                if tweets.includes and 'users' in tweets.includes:
                    users = {user.id: user.username for user in tweets.includes['users']}
                
                for tweet in tweets.data:
                    tweet_text = self.clean_tweet_text(tweet.text)
                    username = users.get(tweet.author_id, 'unknown')
                    found_keywords = extract_keywords(tweet_text)
                    
                    if found_keywords:
                        tweet_data = {
                            'tweet_id': str(tweet.id),
                            'username': username,
                            'content': tweet_text,
                            'created_at': tweet.created_at.isoformat() if tweet.created_at else '',
                            'retweet_count': tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            'like_count': tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            'sentiment_score': analyze_sentiment(tweet_text),
                            'keywords': found_keywords
                        }
                        
                        processed_tweets.append(tweet_data)
            
            return processed_tweets
            
        except Exception as e:
            print(f"Error searching tweets for keywords: {e}")
            return []
    
    def collect_all_tweets(self):
        """Collect tweets from all configured sources."""
        if not self.is_configured():
            print("Twitter API not configured. Skipping tweet collection.")
            return 0
        
        print("Starting Twitter data collection...")
        total_new_tweets = 0
        
        # Fetch from specific accounts
        print("Fetching from fintech influencers...")
        for username in TWITTER_ACCOUNTS:
            try:
                tweets = self.fetch_user_tweets(username, count=20)
                new_tweets = 0
                
                for tweet_data in tweets:
                    if store_tweet(tweet_data):
                        new_tweets += 1
                
                if new_tweets > 0:
                    print(f"✓ @{username}: {new_tweets} new tweets")
                
                total_new_tweets += new_tweets
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"✗ Error fetching tweets from @{username}: {e}")
        
        # Fetch keyword-based tweets
        print("Searching for keyword-based tweets...")
        try:
            keyword_tweets = self.fetch_keyword_tweets(FINTECH_KEYWORDS, count=50)
            new_keyword_tweets = 0
            
            for tweet_data in keyword_tweets:
                if store_tweet(tweet_data):
                    new_keyword_tweets += 1
            
            print(f"✓ Keyword search: {new_keyword_tweets} new tweets")
            total_new_tweets += new_keyword_tweets
            
        except Exception as e:
            print(f"✗ Error fetching keyword tweets: {e}")
        
        print(f"\nTotal new tweets collected: {total_new_tweets}")
        return total_new_tweets

def test_twitter_connection():
    """Test Twitter API connection."""
    client = TwitterClient()
    
    if not client.is_configured():
        print("❌ Twitter API not configured")
        print("To enable Twitter integration:")
        print("1. Go to https://developer.twitter.com/")
        print("2. Create a developer account and app")
        print("3. Copy your credentials to a .env file")
        print("4. See .env.example for the required format")
        return False
    
    try:
        # Test with a simple user lookup
        user = client.client.get_user(username="VitalikButerin")
        if user.data:
            print("✅ Twitter API connection successful!")
            return True
    except Exception as e:
        print(f"❌ Twitter API test failed: {e}")
    
    return False

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Test connection
    if test_twitter_connection():
        # Collect tweets
        client = TwitterClient()
        client.collect_all_tweets()
    else:
        print("Twitter integration disabled. RSS feeds will still work.")