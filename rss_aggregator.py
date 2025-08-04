import feedparser
import requests
from datetime import datetime
import time
from textblob import TextBlob
from bs4 import BeautifulSoup
import re

from config import RSS_FEEDS, FINTECH_KEYWORDS
from database import store_article, init_database

def clean_html(text):
    """Remove HTML tags and clean up text."""
    if not text:
        return ""
    
    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(text, title=""):
    """Extract relevant fintech keywords from text."""
    combined_text = f"{title} {text}".lower()
    found_keywords = []
    
    for keyword in FINTECH_KEYWORDS:
        if keyword.lower() in combined_text:
            found_keywords.append(keyword)
    
    return found_keywords

def analyze_sentiment(text):
    """Analyze sentiment of the text using TextBlob."""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity  # Returns -1 to 1
    except:
        return 0.0

def fetch_rss_feeds():
    """Fetch and process all RSS feeds."""
    print("Starting RSS feed aggregation...")
    total_new_articles = 0
    
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"Fetching from {source_name}...")
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"Warning: RSS feed {source_name} may have issues")
            
            new_articles = 0
            
            for entry in feed.entries:
                # Extract article data
                title = entry.get('title', 'No Title')
                description = clean_html(entry.get('description', '') or entry.get('summary', ''))
                link = entry.get('link', '')
                
                # Get published date
                published_date = entry.get('published', '')
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6]).isoformat()
                    except:
                        pass
                
                # Extract and analyze content
                content = f"{title} {description}"
                keywords = extract_keywords(content, title)
                sentiment_score = analyze_sentiment(content)
                
                # Only store if it contains fintech keywords
                if keywords:
                    article_data = {
                        'title': title,
                        'description': description,
                        'link': link,
                        'source': source_name,
                        'published_date': published_date,
                        'content': content,
                        'sentiment_score': sentiment_score,
                        'keywords': keywords
                    }
                    
                    if store_article(article_data):
                        new_articles += 1
            
            print(f"✓ {source_name}: {new_articles} new articles")
            total_new_articles += new_articles
            
        except Exception as e:
            print(f"✗ Error fetching {source_name}: {e}")
        
        # Be respectful to servers
        time.sleep(1)
    
    print(f"\nTotal new articles collected: {total_new_articles}")
    return total_new_articles

def fetch_full_article_content(url):
    """Attempt to fetch full article content from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try common article content selectors
        content_selectors = [
            'article',
            '.article-content',
            '.post-content', 
            '.entry-content',
            '.content',
            'main',
            '.story-body'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Remove script and style elements
                for script in content_div(["script", "style"]):
                    script.decompose()
                
                text = content_div.get_text()
                # Clean up whitespace
                text = re.sub(r'\n+', '\n', text)
                text = re.sub(r' +', ' ', text)
                return text.strip()
        
        return None
        
    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return None

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Fetch RSS feeds
    fetch_rss_feeds()